#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import json
from mock.mock import MagicMock, call, patch
from stacks.utils.RMFTestCase import *

@patch("os.path.exists", new = MagicMock(return_value=True))
class TestHookAfterInstall(RMFTestCase):

  def test_hook_default(self):

    self.executeScript("2.0.6/hooks/after-INSTALL/scripts/hook.py",
                       classname="AfterInstallHook",
                       command="hook",
                       config_file="default.json"
    )
    self.assertResourceCalled('XmlConfig', 'core-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['core-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
                              only_if="ls /etc/hadoop/conf")

    self.assertNoMoreResources()


  @patch("shared_initialization.load_version", new = MagicMock(return_value="2.3.0.0-1243"))
  @patch("resource_management.libraries.functions.conf_select.create")
  @patch("resource_management.libraries.functions.conf_select.select")
  @patch("os.symlink")
  @patch("shutil.rmtree")
  def test_hook_default_conf_select(self, rmtree_mock, symlink_mock, conf_select_select_mock, conf_select_create_mock):

    def mocked_conf_select(arg1, arg2, arg3, dry_run = False):
      return "/etc/{0}/{1}/0".format(arg2, arg3)

    conf_select_create_mock.side_effect = mocked_conf_select

    config_file = self.get_src_folder() + "/test/python/stacks/2.0.6/configs/default.json"
    with open(config_file, "r") as f:
      json_content = json.load(f)

    version = '2.3.0.0-1234'
    json_content['commandParams']['version'] = version
    json_content['hostLevelParams']['stack_version'] = "2.3"

    self.executeScript("2.0.6/hooks/after-INSTALL/scripts/hook.py",
                       classname="AfterInstallHook",
                       command="hook",
                       config_dict = json_content)


    self.assertResourceCalled('Execute', 'ambari-sudo.sh /usr/bin/hdp-select set all `ambari-python-wrap /usr/bin/hdp-select versions | grep ^2.3 | tail -1` && ambari-sudo.sh [RMF_ENV_PLACEHOLDER] -H -E touch /var/lib/ambari-agent/data/hdp-select-set-all.performed',
        not_if = 'test -f /var/lib/ambari-agent/data/hdp-select-set-all.performed',
        only_if = 'ls -d /usr/hdp/2.3*',
    )

    self.assertResourceCalled('XmlConfig', 'core-site.xml',
      owner = 'hdfs',
      group = 'hadoop',
      conf_dir = "/usr/hdp/current/hadoop-client/conf",
      configurations = self.getConfig()['configurations']['core-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
      only_if="ls /usr/hdp/current/hadoop-client/conf")

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/ranger/kms/conf', '/etc/ranger/kms/conf.install'),
        not_if = 'test -e /etc/ranger/kms/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/ranger/kms/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/ranger/kms/conf',
        to = '/usr/hdp/current/ranger-kms/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/zookeeper/conf', '/etc/zookeeper/conf.install'),
        not_if = 'test -e /etc/zookeeper/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/zookeeper/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/zookeeper/conf',
        to = '/usr/hdp/current/zookeeper-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/pig/conf', '/etc/pig/conf.install'),
        not_if = 'test -e /etc/pig/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/pig/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/pig/conf',
        to = '/usr/hdp/current/pig-client/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/tez/conf', '/etc/tez/conf.install'),
        not_if = 'test -e /etc/tez/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/tez/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/tez/conf',
        to = '/usr/hdp/current/tez-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hive-webhcat/conf', '/etc/hive-webhcat/conf.install'),
        not_if = 'test -e /etc/hive-webhcat/conf.install',
        sudo = True,)
    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hive-hcatalog/conf', '/etc/hive-hcatalog/conf.install'),
        not_if = 'test -e /etc/hive-hcatalog/conf.install',
        sudo = True,)

    self.assertResourceCalled('Directory', '/etc/hive-webhcat/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/hive-webhcat/conf',
        to = '/usr/hdp/current/hive-webhcat/etc/webhcat',)

    self.assertResourceCalled('Directory', '/etc/hive-hcatalog/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/hive-hcatalog/conf',
        to = '/usr/hdp/current/hive-webhcat/etc/hcatalog',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hbase/conf', '/etc/hbase/conf.install'),
        not_if = 'test -e /etc/hbase/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/hbase/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/hbase/conf',
        to = '/usr/hdp/current/hbase-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/knox/conf', '/etc/knox/conf.install'),
        not_if = 'test -e /etc/knox/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/knox/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/knox/conf',
        to = '/usr/hdp/current/knox-server/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/ranger/usersync/conf', '/etc/ranger/usersync/conf.install'),
        not_if = 'test -e /etc/ranger/usersync/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/ranger/usersync/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/ranger/usersync/conf',
        to = '/usr/hdp/current/ranger-usersync/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hadoop/conf', '/etc/hadoop/conf.install'),
        not_if = 'test -e /etc/hadoop/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/hadoop/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/hadoop/conf',
        to = '/usr/hdp/current/hadoop-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/mahout/conf', '/etc/mahout/conf.install'),
        not_if = 'test -e /etc/mahout/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/mahout/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/mahout/conf',
        to = '/usr/hdp/current/mahout-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/storm/conf', '/etc/storm/conf.install'),
        not_if = 'test -e /etc/storm/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/storm/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/storm/conf',
        to = '/usr/hdp/current/storm-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/ranger/admin/conf', '/etc/ranger/admin/conf.install'),
        not_if = 'test -e /etc/ranger/admin/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/ranger/admin/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/ranger/admin/conf',
        to = '/usr/hdp/current/ranger-admin/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/flume/conf', '/etc/flume/conf.install'),
        not_if = 'test -e /etc/flume/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/flume/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/flume/conf',
        to = '/usr/hdp/current/flume-server/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/sqoop/conf', '/etc/sqoop/conf.install'),
        not_if = 'test -e /etc/sqoop/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/sqoop/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/sqoop/conf',
        to = '/usr/hdp/current/sqoop-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/accumulo/conf', '/etc/accumulo/conf.install'),
        not_if = 'test -e /etc/accumulo/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/accumulo/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/accumulo/conf',
        to = '/usr/hdp/current/accumulo-client/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/phoenix/conf', '/etc/phoenix/conf.install'),
        not_if = 'test -e /etc/phoenix/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/phoenix/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/phoenix/conf',
        to = '/usr/hdp/current/phoenix-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/storm-slider-client/conf', '/etc/storm-slider-client/conf.install'),
        not_if = 'test -e /etc/storm-slider-client/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/storm-slider-client/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/storm-slider-client/conf',
        to = '/usr/hdp/current/storm-slider-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/slider/conf', '/etc/slider/conf.install'),
        not_if = 'test -e /etc/slider/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/slider/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/slider/conf',
        to = '/usr/hdp/current/slider-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/oozie/conf', '/etc/oozie/conf.install'),
        not_if = 'test -e /etc/oozie/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/oozie/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/oozie/conf',
        to = '/usr/hdp/current/oozie-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/falcon/conf', '/etc/falcon/conf.install'),
        not_if = 'test -e /etc/falcon/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/falcon/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/falcon/conf',
        to = '/usr/hdp/current/falcon-client/conf')


    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/spark/conf', '/etc/spark/conf.install'),
        not_if = 'test -e /etc/spark/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/spark/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/spark/conf',
        to = '/usr/hdp/current/spark-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/kafka/conf', '/etc/kafka/conf.install'),
        not_if = 'test -e /etc/kafka/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/kafka/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/kafka/conf',
        to = '/usr/hdp/current/kafka-broker/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hive/conf', '/etc/hive/conf.install'),
        not_if = 'test -e /etc/hive/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/hive/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/hive/conf',
        to = '/usr/hdp/current/hive-client/conf')

    self.assertNoMoreResources()

  @patch("shared_initialization.load_version", new = MagicMock(return_value="2.3.0.0-1243"))
  @patch("resource_management.libraries.functions.conf_select.create")
  @patch("resource_management.libraries.functions.conf_select.select")
  @patch("os.symlink")
  @patch("shutil.rmtree")
  def test_hook_default_conf_select_with_error(self, rmtree_mock, symlink_mock, conf_select_select_mock, conf_select_create_mock):

    def mocked_conf_select(arg1, arg2, arg3, dry_run = False):
      if arg2 == "pig" and not dry_run:
        raise Exception("whoops")
      return "/etc/{0}/{1}/0".format(arg2, arg3)

    conf_select_create_mock.side_effect = mocked_conf_select

    conf_select_select_mock.side_effect = mocked_conf_select

    config_file = self.get_src_folder() + "/test/python/stacks/2.0.6/configs/default.json"
    with open(config_file, "r") as f:
      json_content = json.load(f)

    version = '2.3.0.0-1234'
    json_content['commandParams']['version'] = version
    json_content['hostLevelParams']['stack_version'] = "2.3"

    self.executeScript("2.0.6/hooks/after-INSTALL/scripts/hook.py",
                       classname="AfterInstallHook",
                       command="hook",
                       config_dict = json_content)


    self.assertResourceCalled('Execute', 'ambari-sudo.sh /usr/bin/hdp-select set all `ambari-python-wrap /usr/bin/hdp-select versions | grep ^2.3 | tail -1` && ambari-sudo.sh [RMF_ENV_PLACEHOLDER] -H -E touch /var/lib/ambari-agent/data/hdp-select-set-all.performed',
        not_if = 'test -f /var/lib/ambari-agent/data/hdp-select-set-all.performed',
        only_if = 'ls -d /usr/hdp/2.3*',
    )

    self.assertResourceCalled('XmlConfig', 'core-site.xml',
      owner = 'hdfs',
      group = 'hadoop',
      conf_dir = "/usr/hdp/current/hadoop-client/conf",
      configurations = self.getConfig()['configurations']['core-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
      only_if="ls /usr/hdp/current/hadoop-client/conf")

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/ranger/kms/conf', '/etc/ranger/kms/conf.install'),
        not_if = 'test -e /etc/ranger/kms/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/ranger/kms/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/ranger/kms/conf',
        to = '/usr/hdp/current/ranger-kms/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/zookeeper/conf', '/etc/zookeeper/conf.install'),
        not_if = 'test -e /etc/zookeeper/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/zookeeper/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/zookeeper/conf',
        to = '/usr/hdp/current/zookeeper-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/pig/conf', '/etc/pig/conf.install'),
        not_if = 'test -e /etc/pig/conf.install',
        sudo = True,)
    # pig fails, so no Directory/Link combo

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/tez/conf', '/etc/tez/conf.install'),
        not_if = 'test -e /etc/tez/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/tez/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/tez/conf',
        to = '/usr/hdp/current/tez-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hive-webhcat/conf', '/etc/hive-webhcat/conf.install'),
        not_if = 'test -e /etc/hive-webhcat/conf.install',
        sudo = True,)
    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hive-hcatalog/conf', '/etc/hive-hcatalog/conf.install'),
        not_if = 'test -e /etc/hive-hcatalog/conf.install',
        sudo = True,)

    self.assertResourceCalled('Directory', '/etc/hive-webhcat/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/hive-webhcat/conf',
        to = '/usr/hdp/current/hive-webhcat/etc/webhcat',)

    self.assertResourceCalled('Directory', '/etc/hive-hcatalog/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/hive-hcatalog/conf',
        to = '/usr/hdp/current/hive-webhcat/etc/hcatalog',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hbase/conf', '/etc/hbase/conf.install'),
        not_if = 'test -e /etc/hbase/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/hbase/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/hbase/conf',
        to = '/usr/hdp/current/hbase-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/knox/conf', '/etc/knox/conf.install'),
        not_if = 'test -e /etc/knox/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/knox/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/knox/conf',
        to = '/usr/hdp/current/knox-server/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/ranger/usersync/conf', '/etc/ranger/usersync/conf.install'),
        not_if = 'test -e /etc/ranger/usersync/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/ranger/usersync/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/ranger/usersync/conf',
        to = '/usr/hdp/current/ranger-usersync/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hadoop/conf', '/etc/hadoop/conf.install'),
        not_if = 'test -e /etc/hadoop/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/hadoop/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/hadoop/conf',
        to = '/usr/hdp/current/hadoop-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/mahout/conf', '/etc/mahout/conf.install'),
        not_if = 'test -e /etc/mahout/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/mahout/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/mahout/conf',
        to = '/usr/hdp/current/mahout-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/storm/conf', '/etc/storm/conf.install'),
        not_if = 'test -e /etc/storm/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/storm/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/storm/conf',
        to = '/usr/hdp/current/storm-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/ranger/admin/conf', '/etc/ranger/admin/conf.install'),
        not_if = 'test -e /etc/ranger/admin/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/ranger/admin/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/ranger/admin/conf',
        to = '/usr/hdp/current/ranger-admin/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/flume/conf', '/etc/flume/conf.install'),
        not_if = 'test -e /etc/flume/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/flume/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/flume/conf',
        to = '/usr/hdp/current/flume-server/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/sqoop/conf', '/etc/sqoop/conf.install'),
        not_if = 'test -e /etc/sqoop/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/sqoop/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/sqoop/conf',
        to = '/usr/hdp/current/sqoop-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/accumulo/conf', '/etc/accumulo/conf.install'),
        not_if = 'test -e /etc/accumulo/conf.install',
        sudo = True,)
    self.assertResourceCalled('Directory', '/etc/accumulo/conf',
        action = ['delete'],)
    self.assertResourceCalled('Link', '/etc/accumulo/conf',
        to = '/usr/hdp/current/accumulo-client/conf',)

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/phoenix/conf', '/etc/phoenix/conf.install'),
        not_if = 'test -e /etc/phoenix/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/phoenix/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/phoenix/conf',
        to = '/usr/hdp/current/phoenix-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/storm-slider-client/conf', '/etc/storm-slider-client/conf.install'),
        not_if = 'test -e /etc/storm-slider-client/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/storm-slider-client/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/storm-slider-client/conf',
        to = '/usr/hdp/current/storm-slider-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/slider/conf', '/etc/slider/conf.install'),
        not_if = 'test -e /etc/slider/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/slider/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/slider/conf',
        to = '/usr/hdp/current/slider-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/oozie/conf', '/etc/oozie/conf.install'),
        not_if = 'test -e /etc/oozie/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/oozie/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/oozie/conf',
        to = '/usr/hdp/current/oozie-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/falcon/conf', '/etc/falcon/conf.install'),
        not_if = 'test -e /etc/falcon/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/falcon/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/falcon/conf',
        to = '/usr/hdp/current/falcon-client/conf')


    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/spark/conf', '/etc/spark/conf.install'),
        not_if = 'test -e /etc/spark/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/spark/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/spark/conf',
        to = '/usr/hdp/current/spark-client/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/kafka/conf', '/etc/kafka/conf.install'),
        not_if = 'test -e /etc/kafka/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/kafka/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/kafka/conf',
        to = '/usr/hdp/current/kafka-broker/conf')

    self.assertResourceCalled('Execute', ('cp', '-R', '-p', '/etc/hive/conf', '/etc/hive/conf.install'),
        not_if = 'test -e /etc/hive/conf.install',
        sudo = True)
    self.assertResourceCalled('Directory', '/etc/hive/conf',
        action = ['delete'])
    self.assertResourceCalled('Link', '/etc/hive/conf',
        to = '/usr/hdp/current/hive-client/conf')

    self.assertNoMoreResources()
