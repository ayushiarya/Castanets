#!/usr/bin/env python
#
# Copyright 2019 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Takes a netlog for the WebViews in a given application.

Developer guide:
https://chromium.googlesource.com/chromium/src/+/HEAD/android_webview/docs/net-debugging.md
"""

from __future__ import print_function

import argparse
import logging
import os
import re
import sys
import time

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, 'build', 'android'))
import devil_chromium  # pylint: disable=import-error
from devil.android import device_errors  # pylint: disable=import-error
from devil.android import flag_changer  # pylint: disable=import-error
from devil.android import device_utils  # pylint: disable=import-error
from devil.android.tools import script_common  # pylint: disable=import-error
from devil.utils import logging_common  # pylint: disable=import-error

WEBVIEW_COMMAND_LINE = 'webview-command-line'


def _WaitUntilCtrlC():
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print()  # print a new line after the "^C" the user typed to the console


def CheckAppNotRunning(device, package_name, force):
  processes = device.ListProcesses(package_name)
  if processes:
    msg = ('Netlog requires setting commandline flags, which only works if the '
           'application ({}) is not already running. Please kill the app and '
           'restart the script.'.format(
               package_name))
    if force:
      logging.warning(msg)
    else:
      # Extend the sentence to mention the user can skip the check.
      msg = re.sub(r'\.$', ', or pass --force to ignore this check.', msg)
      raise RuntimeError(msg)


def main():
  parser = argparse.ArgumentParser(description="""
Configures WebView to start recording a netlog. This script chooses a suitable
netlog filename for the application, and will pull the netlog off the device
when the user terminates the script (with ctrl-C). For a more complete usage
guide, open your web browser to:
https://chromium.googlesource.com/chromium/src/+/HEAD/android_webview/docs/net-debugging.md
""")
  parser.add_argument(
      '--package',
      required=True,
      type=str,
      help='Package name of the application you intend to use.')
  parser.add_argument(
      '--force',
      default=False,
      action='store_true',
      help='Suppress user checks.')

  script_common.AddEnvironmentArguments(parser)
  script_common.AddDeviceArguments(parser)
  logging_common.AddLoggingArguments(parser)

  args = parser.parse_args()
  logging_common.InitializeLogging(args)
  devil_chromium.Initialize()
  script_common.InitializeEnvironment(args)

  # Only use a single device, for the sake of simplicity (of implementation and
  # user experience).
  devices = device_utils.DeviceUtils.HealthyDevices(device_arg=args.devices)
  device = devices[0]
  if len(devices) > 1:
    raise device_errors.MultipleDevicesError(devices)

  package_name = args.package
  device_netlog_file_name = 'netlog.json'
  device_netlog_path = os.path.join(
      device.GetApplicationDataDirectory(package_name), 'app_webview',
      device_netlog_file_name)

  CheckAppNotRunning(device, package_name, args.force)

  # Append to the existing flags, to allow users to experiment with other
  # features/flags enabled. The CustomCommandLineFlags will restore the original
  # flag state after the user presses 'ctrl-C'.
  changer = flag_changer.FlagChanger(device, WEBVIEW_COMMAND_LINE)
  new_flags = changer.GetCurrentFlags()
  new_flags.append('--log-net-log={}'.format(device_netlog_path))

  logging.info('Running with flags %r', new_flags)
  with flag_changer.CustomCommandLineFlags(device, WEBVIEW_COMMAND_LINE,
                                           new_flags):
    print('Netlog will start recording as soon as app starts up. Press ctrl-C '
          'to stop recording.')
    _WaitUntilCtrlC()

  host_netlog_path = 'netlog.json'
  print('Pulling netlog to "%s"' % host_netlog_path)
  # The netlog file will be under the app's uid, which the default shell doesn't
  # have permission to read (but root does). Prefer this to EnableRoot(), which
  # restarts the adb daemon.
  device.PullFile(device_netlog_path, host_netlog_path, as_root=True)
  device.RemovePath(device_netlog_path, as_root=True)


if __name__ == '__main__':
  main()
