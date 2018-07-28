using System;
using System.IO;
using System.Linq;

namespace CSprojectReferenceSwitchTool
{
    class Program
    {
        static void Main(string[] args)
        {
            var baseDir = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
            var allCsprojectsFiles = baseDir.GetFiles("*.csproj", SearchOption.AllDirectories).ToList();

            if (args.Any())
            {
                foreach (var arg in args)
                {
                    var dir = new DirectoryInfo(arg);

                    if (dir.Exists)
                    {
                        allCsprojectsFiles = allCsprojectsFiles.Where(s => !s.FullName.Contains(dir.FullName)).ToList();
                    }
                }
            }
        }
    }
}
