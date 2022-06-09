""" 
    Wrapper to carmensystems.common.ServiceConfig used to convert unicode to string
"""
import subprocess

from carmensystems.common.ServiceConfig import ServiceConfig

class ServiceConfig(ServiceConfig):
            
    def getProperty(self, *args, **kwargs):
        key, value = super(ServiceConfig, self).getProperty(*args, **kwargs)
	if key is None or value is None:
	    return key, value
	return (str(key), str(value))
    
    def __getattr__(self, attr):
        print "inside getattr %s" % attr
    
    def getProperties(self, *args, **kwargs):
        properties = super(ServiceConfig, self).getProperties(*args, **kwargs)
            
        encoded = [tuple([str(s) for s in t]) for t in properties]
        return encoded
        return map(str, super(ServiceConfig, self).getProperties(*args, **kwargs))
        
    def getPropertyValue(self, *args, **kwargs):
        val = super(ServiceConfig, self).getPropertyValue(*args, **kwargs)
	if val is None:
	    return None
        return str(val)

    def getServiceUrl(self, *args, **kwargs):
        url = super(ServiceConfig, self).getServiceUrl(*args, **kwargs)
	if url is None:
	    return None
        return str(url)
    
    def _execute_cmd(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out
    
    def _split_service_string(self, key, line, start_pos):
        if key == 'service':
            delimiter = '/'
        elif key == 'process':
            delimiter = '@'
        elif key == 'node':
            delimiter = ' ='
        elif key == 'url':
            delimiter = '= '
        end_pos = line.find(delimiter, start_pos)
        if end_pos < start_pos:
            end_pos = len(line)
        line = line[start_pos:end_pos]
        
        return line.lstrip().rstrip(), end_pos + len(delimiter)
        
    def getServices(self):
        output = self._execute_cmd(['xmlconfig', '--srv'])
        srv = []
        for line in iter(output.splitlines()):
            start_pos = 0
            service, start_pos = self._split_service_string('service', line, start_pos)
            process, start_pos = self._split_service_string('process', line, start_pos)
            node, start_pos = self._split_service_string('node', line, start_pos)
            url, start_pos = self._split_service_string('url', line, start_pos)
            srv.append((service, process, node, url))
        return srv
