using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace CSprojectReferenceSwitchTool
{
    class Program
    {
        static void Main(string[] args)
        {
            var baseDir = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            var csprojectsFiles = baseDir.GetFiles("*.csproj", SearchOption.AllDirectories).ToList();

            if (args.Any())
            {
                foreach (var arg in args)
                {
                    var dir = new DirectoryInfo(arg);

                    if (dir.Exists)
                    {
                        csprojectsFiles = csprojectsFiles.Where(s => !s.FullName.Contains(dir.FullName)).ToList();
                    }
                }
            }

            Parallel.ForEach(csprojectsFiles, csprojectsFile =>
            {
                var csProject = new CsProjectFile(csprojectsFile);
                csProject.SwitchReferences();
            });

            Console.WriteLine("switch all references");
        }
    }
}
