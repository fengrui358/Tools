using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Threading.Tasks;

namespace PortsScan
{
    public class Program
    {
        private static string _scanIp = "122.114.52.11";
        private static List<int> _ports = new List<int>();

        private static readonly ConcurrentDictionary<Task, Tuple<TcpClient, int>> Tasks = new ConcurrentDictionary<Task, Tuple<TcpClient, int>>();
        private static ConcurrentBag<int> _openPorts = new ConcurrentBag<int>();

        public static void Main(string[] args)
        {
            var ip = GetIp(args);

            if (IsIp(ip))
            {
                _scanIp = ip;

                var ports = GetPorts(args);
                _ports = ConvertPorts(ports).ToList();
            }

            while (!IsIp(_scanIp))
            {
                Console.WriteLine("input ip address");

                var input = Console.ReadLine();
                if (IsIp(input))
                {
                    _scanIp = input;
                }
            }

            while (!_ports.Any())
            {
                Console.WriteLine("input ports,can be a range(1-65535) or all(*)");

                var input = Console.ReadLine();
                _ports = ConvertPorts(input).ToList();
            }

            Console.WriteLine("Scan...");

            //开始扫描
            Parallel.ForEach(_ports, (port, state) =>
            {
                var tcpClient = new TcpClient();

                try
                {
                    var task = tcpClient.ConnectAsync(_scanIp, port);

                    Tasks.TryAdd(task, new Tuple<TcpClient, int>(tcpClient, port));
                    //task.Wait();

                    //if (tcpClient.Connected)
                    //{
                    //    _openPorts.Add(port);
                    //}
                }
                catch
                {
                    // ignored
                }
                //finally
                //{
                //    tcpClient.Dispose();
                //}
            });

            while (Tasks.Any())
            {
                var over = new List<Task>();
                foreach (var tcpClient in Tasks)
                {
                    var task = tcpClient.Key;
                    if (task.IsCompleted || task.IsCanceled || task.IsFaulted)
                    {
                        if (tcpClient.Value.Item1.Connected)
                        {
                            _openPorts.Add(tcpClient.Value.Item2);

                            Console.Write($"{tcpClient.Value.Item2}  ");
                        }
                    }
                }

                foreach (var task in over)
                {
                    Tuple<TcpClient, int> r;
                    if (Tasks.TryRemove(task, out r))
                    {
                        r.Item1.Dispose();
                    }
                }
            }

            //Console.WriteLine("result:");

            //var opens = _openPorts.ToList().OrderBy(s => s).ToList();

            //for (int i = 0; i < opens.Count(); i++)
            //{
            //    if (i != opens.Count() - 1)
            //    {
            //        Console.WriteLine($"{opens[i]}");
            //    }
            //    else
            //    {
            //        Console.Write(opens[i]);
            //    }
            //}

            Console.ReadKey();
        }

        private static string GetIp(string[] args)
        {
            var ipIndex = -1;

            for (int i = 0; i < args.Length; i++)
            {
                if (i == ipIndex)
                {
                    return args[i];
                }

                var isIpCommand = args[i].Equals("-ip", StringComparison.OrdinalIgnoreCase);
                if (isIpCommand)
                {
                    ipIndex = i + 1;
                }
            }

            return String.Empty;
        }

        private static bool IsIp(string ip)
        {
            if (!string.IsNullOrEmpty(ip))
            {
                IPAddress ipAddress;
                if (IPAddress.TryParse(ip, out ipAddress))
                {
                    return true;
                }
            }

            return false;
        }

        private static string GetPorts(string[] args)
        {
            var ipIndex = -1;

            for (int i = 0; i < args.Length; i++)
            {
                if (i == ipIndex)
                {
                    return args[i];
                }

                var isIpCommand = args[i].Equals("-ports", StringComparison.OrdinalIgnoreCase);
                if (isIpCommand)
                {
                    ipIndex = i + 1;
                }
            }

            return String.Empty;
        }

        private static IEnumerable<int> ConvertPorts(string ports)
        {
            var result = new List<int>();
            
            if (!string.IsNullOrEmpty(ports))
            {
                //判断是否为全部
                if (ports.Contains('*'))
                {
                    for (int i = 1; i <= 65535; i++)
                    {
                        result.Add(i);
                    }
                }
                //判断是否是范围
                else if (ports.Contains('-'))
                {
                    var portMinMax = ports.Split('-');
                    if (portMinMax.Length == 2)
                    {
                        var port1 = portMinMax[0];
                        var port2 = portMinMax[1];

                        int portInt1;
                        int portInt2;

                        if (int.TryParse(port1, out portInt1) && int.TryParse(port2, out portInt2))
                        {
                            var minPort = portInt1 <= portInt2 ? portInt1 : portInt2;
                            if (!IsVolidPort(minPort))
                            {
                                minPort = 1;
                            }

                            var maxPort = portInt1 >= portInt2 ? portInt1 : portInt2;
                            if (!IsVolidPort(maxPort))
                            {
                                maxPort = 65535;
                            }

                            for (int i = minPort; i <= maxPort; i++)
                            {
                                result.Add(i);
                            }
                        }
                    }
                }
                //离散
                else if(ports.Contains(","))
                {
                    var portsString = ports.Split(',');
                    foreach (var s in portsString)
                    {
                        int portInt;
                        if (int.TryParse(s, out portInt) && IsVolidPort(portInt))
                        {
                            result.Add(portInt);
                        }
                    }
                }
                //独立
                else
                {
                    int portInt;
                    if (int.TryParse(ports, out portInt) && IsVolidPort(portInt))
                    {
                        result.Add(portInt);
                    }
                }
            }

            return result;
        }

        private static bool IsVolidPort(int port)
        {
            return port >= 1 && port <= 65535;
        }
    }
}
