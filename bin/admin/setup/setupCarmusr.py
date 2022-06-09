import xml.dom.minidom as minidom
import os
import sys
import shutil
import subprocess

##### TODO ####
# comment code

class SetupHandler:
    def __init__(self, config_xml):
        '''
        Read the configuration file and initiates all setup jobs
        
        @param config_xml: The configuration file
        '''
        try:
            proc = subprocess.Popen(['xmllint','--noent', config_xml],
                                      stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            config = minidom.parseString(output)
        except:
            print "Couldn't find config file '%s'" % config_xml
            sys.exit(1)
        
        #Set variables before initiating the setup jobs
        self.setVariables(config)
        
        self.setupJobs = []
        self.initDirectories(config)
        self.initCopies(config)
        self.initSymLinks(config)
        self.initScripts(config)
        self.initRulsets(config)

    def setupSystem(self):
        '''
        Executes all setup jobs
        '''
        for job in self.setupJobs:
            job.handle()
    
    def showSystemConfig(self):
        for job in self.setupJobs:
            print repr(job)

    def setVariables(self, config):
        '''
        Set environment variables to be used during the setup jobs
        
        @param config: the configuration xml
        '''
        for variables_elem in config.getElementsByTagName('variables'):
            variables = variables_elem.getElementsByTagName('variable')
            for variable in variables:
                var = Variable(variable)
                var.handle()

    def initCopies(self, config):
        '''
        Initiates all copy setup jobs
        
        @param config: the configuration xml
        '''
        for copies_elem in config.getElementsByTagName('copies'):
            copies = copies_elem.getElementsByTagName('copy')
            for copy in copies:
                self.setupJobs.append(Copy(copy))

    def initDirectories(self, config):
        '''
        Initiates all directory setup jobs
        
        @param config: the configuration xml
        '''
        for directories_elem in config.getElementsByTagName('directories'):
            directories = directories_elem.getElementsByTagName('directory')        
            for directory in directories:
                self.setupJobs.append(Directory(directory))

    def initSymLinks(self, config):
        '''
        Initiates all symlink setup jobs
        
        @param config: the configuration xml
        '''
        for symlinks_elem in config.getElementsByTagName('symlinks'):
            symlinks = symlinks_elem.getElementsByTagName('symlink')
            for symlink in symlinks:
                self.setupJobs.append(SymLink(symlink))
        
    def initScripts(self, config):
        '''
        Initiates all scripts setup jobs
        
        @param config: the configuration xml
        '''
        for scripts_elem in config.getElementsByTagName('scripts'):
            scripts = scripts_elem.getElementsByTagName('script')
            for script in scripts:
                self.setupJobs.append(Script(script))
        
    def initRulsets(self, config):
        '''
        Initiates all compile ruleset setup jobs
        
        @param config: the configuration xml
        '''
        for rulesets_elem in config.getElementsByTagName('rulesets'):
            rulesets = rulesets_elem.getElementsByTagName('ruleset')
            for ruleset in rulesets:
                self.setupJobs.append(CompileRuleset(ruleset))


class SetupJob:
    def __init__(self, xml_node):
        '''
        The init function should extract the data from the xml node and
        exit the setup script if anything is wrong.
        
        @param xml_node: xml node with attributes specifying the setup job 
        '''
        raise NotImplementedError("Implement __init__ function!")
    
    def handle(self):
        '''
        The handle function executes the setup of the job.
        '''
        raise NotImplementedError("Implement handle function!")

    def absolutePath(self, path):
        '''
        Expands and normalizes a path
        
        @param path: the path to be handled
        @return: the resulting path
        '''
        return os.path.normpath(os.path.expandvars(path))
    
    def endScript(self, reason, status=1):
        '''
        End the setup script due to some setup job problem/reason
        
        @param reason: a string describing what went wrong
        @param status: With what status the script should end (defualt=1)
        '''
        print 'ERROR: %s' % reason
        
        if not '--nocheck' in sys.argv:
            sys.exit(status)
        else:
            print

class Variable(SetupJob):
    def __init__(self, xml_node):
        if not (xml_node.hasAttribute('name') and xml_node.hasAttribute('value')):
            print "Variables need 'name' and 'value' attributes"
            sys.exit(1)
        
        if xml_node.hasAttribute('new'):
            new = xml_node.getAttribute('new') == 'True'
        else:
            new = False
        
        self.name = xml_node.getAttribute('name')
        self.value = self.absolutePath(xml_node.getAttribute('value'))
        
        if new and not os.environ.has_key(self.name):
            self.endScript("Variable '%s' must exist to be replaced" % self.name)
        elif not new and os.environ.has_key(self.name):
            self.endScript("Variable '%s' already exists" % self.name)
    
    def handle(self):
        os.environ[self.name] = self.value
    
    def __repr__(self):
        return "Variable(<name='%s' value='%s'>)" % (self.name, self.value)

    def __str__(self):
        return '$%s="%s"' % (self.name, self.value)

class Copy(SetupJob):
    def __init__(self, xml_node):
        if not (xml_node.hasAttribute('target') and xml_node.hasAttribute('source')):
            print "Directories need 'source' and 'target' attributes"
            sys.exit(1)
        
        if xml_node.hasAttribute('clean'):
            clean = xml_node.getAttribute('clean') == 'True'
        else:
            clean = False
        self.clean = clean
        
        self.target = xml_node.getAttribute('target')
        self.target = self.absolutePath(self.target)

        self.source = xml_node.getAttribute('source')
        self.source = self.absolutePath(self.source)

        self.sourceIsFile = os.path.isfile(self.source)

        if not os.path.exists(self.source):
            self.endScript("Source '%s' doesn't exist" % self.source)

    def handle(self):
        if os.path.exists(self.target) and os.path.samefile(self.source, self.target):
            return        
        
        if os.path.exists(self.target) and not self.clean:
            return
        elif os.path.isdir(self.target):
            shutil.rmtree(self.target)
        elif os.path.isfile(self.target):
            os.remove(self.target)
        
        if self.sourceIsFile:
            shutil.copy(self.source, self.target)
        else:
            shutil.copytree(self.source, self.target)

    def __repr__(self):
        return "Copy(<source='%s' target='%s'>)" % (self.source, self.target)

    def __str__(self):
        return 'cp %s %s' % (self.source, self.target)

class Directory(SetupJob):
    def __init__(self, xml_node):
        if not (xml_node.hasAttribute('path')):
            print "Directories need a 'path' attribute"
            sys.exit(1)
        
        if xml_node.hasAttribute('clean'):
            clean = xml_node.getAttribute('clean') == 'True'
        else:
            clean = False
        self.clean = clean

        self.path = xml_node.getAttribute('path')
        self.path = self.absolutePath(self.path)
        
        if not os.path.isdir(self.path) and os.path.exists(self.path):
            self.endScript("'%s' exists and is not a directory!" % self.path)

    def handle(self):
        if os.path.isdir(self.path):
            if self.clean:
                if os.path.islink(self.path):
                    os.unlink(self.path)
                else:
                    shutil.rmtree(self.path)
            else:
                return
        
        os.makedirs(self.path)

    def __repr__(self):
        return "Directory(<path='%s' clean='%s'>)" % (self.path, self.clean)

    def __str__(self):
        return self.path

class SymLink(SetupJob):
    def __init__(self, xml_node):
        if not (xml_node.hasAttribute('name') and xml_node.hasAttribute('target')):
            print "Symlinks need 'name' and 'target' attributes"
            sys.exit(1)

        self.name = xml_node.getAttribute('name')
        self.name = self.absolutePath(self.name)
        
        self.target = xml_node.getAttribute('target')
        self.target = self.absolutePath(self.target)

        if xml_node.hasAttribute('check'):
            self.check = xml_node.getAttribute('check') == 'True'
        else:
            self.check = False

        if self.check and not os.path.exists(self.target):
            self.endScript("Target '%s' doesn't exist" % self.target)
        
        if os.path.exists(self.name) and not os.path.islink(self.name):
            self.endScript("Name '%s' already exists and is not a symlink" % self.target)

    def handle(self):
        if os.path.islink(self.name):
            os.unlink(self.name)

        os.symlink(self.target, self.name)

    def __repr__(self):
        return "SymLink(<name='%s' target='%s' check='%s'>)" % (self.name, self.target, self.check)

    def __str__(self):
        return '%s -> %s' % (self.name, self.target)

class Script(SetupJob):
    def __init__(self, xml_node):
        if not (xml_node.hasAttribute('path')):
            print "Script need 'path' attribute"
            sys.exit(1)

        self.path = xml_node.getAttribute('path')
        self.path = self.absolutePath(self.path)
        
        if not os.path.isfile(self.path):
            self.endScript("Script '%s' does not exist" % self.path)

    def handle(self):
        ret = subprocess.call(self.path)
        
        if ret != 0:
            self.endScript("problem found in script %s" % self.path)

    def __repr__(self):
        return "Script(<path='%s'>)" % self.path

    def __str__(self):
        return 'exec %s' % self.path

class CompileRuleset(SetupJob):
    def __init__(self, xml_node):
        if not (xml_node.hasAttribute('application')):
            print "CompileRuleset need 'application' attribute"
            sys.exit(1)
        
        self.application = xml_node.getAttribute('application')
    
    def handle(self):
        ret = subprocess.call(['bin/admin/compile_rulesets.sh','-l',self.application])
        
        if ret != 0:
            self.endScript("Couldn't compile %s" % self.application)
    
    def __repr__(self):
        return "CompileRuleset(<application='%s'>)" % self.application
    
    def __str__(self):
        return 'bin/admin/compile_rulesets.sh ' + self.application

def main():
    try:
        config_file = os.environ['CARMSYSTEMNAME'] + '.xml'
    except KeyError:
        config_file = 'default.xml'
    
    if not os.path.exists(os.path.join(os.path.dirname(__file__), config_file)):
        print "No configuration file '%s' found!" % config_file
        sys.exit(1)
    
    config_xml = os.path.join(os.path.dirname(__file__), config_file)
    
    sh = SetupHandler(config_xml)
    
    if '-s' in sys.argv:
        sh.showSystemConfig()
    
    if not '-d' in sys.argv:
        sh.setupSystem()
   
if __name__=='__main__':
    main()
