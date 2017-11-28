#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import ConfigParser
import os
import re
from time import time
import pymysql.cursors

try:
    import json
except ImportError:
    import simplejson as json

from six import iteritems

class MySQLInventory(object):

    def __init__(self):

        """ Main execution path """
        self.conn = None

        self.inventory = dict()  # A list of groups and the hosts in that group
        self.cache = dict()  # Details about hosts in the inventory

        # Read settings and parse CLI arguments
        self.read_settings()
        self.parse_cli_args()

        # Cache
        if self.args.refresh_cache:
            self.update_cache()
        elif not self.is_cache_valid():
            self.update_cache()
        else:
            self.load_inventory_from_cache()
            self.load_cache_from_cache()

        data_to_print = ""

        # Data to print
        if self.args.host:
            data_to_print += self.get_host_info()
        else:
            self.inventory['_meta'] = { 'hostvars': {} }
            for hostname in self.cache:
                self.inventory['_meta']['hostvars'][hostname] = self.cache[hostname]
            data_to_print += self.json_format_dict(self.inventory, True)

        print(data_to_print)

    def _connect(self):
        if not self.conn:
            self.conn = pymysql.connect(**self.myconfig)

    def is_cache_valid(self):
        """ Determines if the cache files have expired, or if it is still valid """

        if os.path.isfile(self.cache_path_cache):
            mod_time = os.path.getmtime(self.cache_path_cache)
            current_time = time()
            if (mod_time + self.cache_max_age) > current_time:
                if os.path.isfile(self.cache_path_inventory):
                    return True

        return False

    def read_settings(self):
        """ Reads the settings from the mysql.ini file """

        config = ConfigParser.SafeConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + '../config.ini')

        self.myconfig = dict(config.items('inventory'))
        if 'port' in self.myconfig:
            self.myconfig['port'] = config.getint('inventory', 'port')

        # Cache related
        cache_path = config.get('inventory', 'inventory_cache_dir')
        self.cache_path_cache = cache_path + "/ansible-mysql.cache"
        self.cache_path_inventory = cache_path + "/ansible-mysql.index"
        self.cache_max_age = config.getint('inventory', 'inventory_cache_max_age')

        # Other config
        self.facts_hostname_var = config.get('inventory', 'facts_hostname_var')

    def parse_cli_args(self):
        """ Command line argument processing """

        parser = argparse.ArgumentParser(description='Produce an Ansible Inventory file based on MySQL')
        parser.add_argument('--list', action='store_true', default=True, help='List instances (default: True)')
        parser.add_argument('--host', action='store', help='Get all the variables about a specific instance')
        parser.add_argument('--refresh-cache', action='store_true', default=False,
                            help='Force refresh of cache by making API requests to MySQL (default: False - use cache files)')
        self.args = parser.parse_args()

    def process_group(self, groupname):
        # Fetch the Group info
        if groupname not in self.inventory:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT variables FROM `group` WHERE name = %s"
            cursor.execute(sql, groupname)
            groupinfo = cursor.fetchone()
            self.inventory[groupname] = dict()
            if groupinfo['variables'] and groupinfo['variables'].strip():
                try:
                   self.inventory[groupname]['vars'] = json.loads(groupinfo['variables'])
                   self.inventory[groupname]['hosts'] = list()
                except:
                   raise Exception('Group does not have valid JSON', groupname, groupinfo['variables'])

            if 'vars' not in self.inventory[groupname]:
               self.inventory[groupname] = list()

    def update_cache(self):
        """ Make calls to MySQL and save the output in a cache """

        self._connect()
        self.hosts = dict()

        # Fetch the systems
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM inventory;"
        cursor.execute(sql)
        data = cursor.fetchall()

        for host in data:
            self.process_group(host['group'])

            if 'hosts' in self.inventory[host['group']]:
                self.inventory[host['group']]['hosts'].append(host['host'])
            else:
                self.inventory[host['group']].append(host['host'])

            dns_name = host['host']
            if host['host_vars'] and host['host_vars'].strip():
                try:
                   cleanhost = json.loads(host['host_vars'])
                except:
                   raise Exception('Host does not have valid JSON', host['host'], host['host_vars'])
            else:
                cleanhost = dict()
            cleanhost[self.facts_hostname_var] = host['hostname']

            self.cache[dns_name] = cleanhost
            self.inventory = self.inventory

        # first fetch all the groups to check for possible childs
        gsql = """SELECT
               `gparent`.`name` as `parent`,
               `gchild`.`name` as `child`
               FROM childgroups
               LEFT JOIN `group` `gparent` on `childgroups`.`parent_id` = `gparent`.`id`
               LEFT JOIN `group` `gchild` on `childgroups`.`child_id` = `gchild`.`id`
               ORDER BY `parent`;"""

        cursor.execute(gsql)
        groupdata = cursor.fetchall()

        for group in groupdata:
            self.process_group(group['parent'])
            if 'hosts' not in self.inventory[group['parent']]:
                self.inventory[group['parent']] = {'hosts': self.inventory[group['parent']]}

            if 'children' not in self.inventory[group['parent']]:
                self.inventory[group['parent']]['children'] = list()

            self.inventory[group['parent']]['children'].append(group['child'])

        # cleanup output
        for group in self.inventory:
            if not self.inventory[group]['hosts']:
                del self.inventory[group]['hosts']

        self.write_to_cache(self.cache, self.cache_path_cache)
        self.write_to_cache(self.inventory, self.cache_path_inventory)

    def get_host_info(self):
        """ Get variables about a specific host """

        if not self.cache or len(self.cache) == 0:
            # Need to load index from cache
            self.load_cache_from_cache()

        if not self.args.host in self.cache:
            # try updating the cache
            self.update_cache()

            if not self.args.host in self.cache:
                # host might not exist anymore
                return self.json_format_dict({}, True)

        return self.json_format_dict(self.cache[self.args.host], True)

    def push(self, my_dict, key, element):
        """ Pushed an element onto an array that may not have been defined in the dict """

        if key in my_dict:
            my_dict[key].append(element)
        else:
            my_dict[key] = [element]

    def load_inventory_from_cache(self):
        """ Reads the index from the cache file sets self.index """

        cache = open(self.cache_path_inventory, 'r')
        json_inventory = cache.read()
        self.inventory = json.loads(json_inventory)

    def load_cache_from_cache(self):
        """ Reads the cache from the cache file sets self.cache """

        cache = open(self.cache_path_cache, 'r')
        json_cache = cache.read()
        self.cache = json.loads(json_cache)

    def write_to_cache(self, data, filename):
        """ Writes data in JSON format to a file """
        json_data = self.json_format_dict(data, True)
        cache = open(filename, 'w')
        cache.write(json_data)
        cache.close()

    def to_safe(self, word):
        """ Converts 'bad' characters in a string to underscores so they can be used as Ansible groups """

        return re.sub("[^A-Za-z0-9\-]", "_", word)

    def json_format_dict(self, data, pretty=False):
        """ Converts a dict to a JSON object and dumps it as a formatted string """

        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
        else:
            return json.dumps(data)

MySQLInventory()
