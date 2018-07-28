using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;

namespace CSprojectReferenceSwitchTool
{
    public class CsProjectFile
    {
        public FileInfo FileInfo { get; private set; }

        public List<FileInfo> LocalReferenceList { get; private set; }

        public CsProjectFile(FileInfo fileInfo)
        {
            FileInfo = fileInfo ?? throw new ArgumentNullException(nameof(fileInfo));

            LocalReferenceList = DotnetHelper.GetLocalReferenceList(FileInfo);
        }

        /// <summary>
        /// 获取包名
        /// </summary>
        /// <param name="fileInfo"></param>
        /// <returns></returns>
        public static string GetPackageName(FileInfo fileInfo)
        {
            var packageName = string.Empty;

            if (fileInfo.Exists)
            {
                var fileContent = File.ReadAllText(fileInfo.FullName);

                var match = Regex.Match(fileContent, "(?<=<PackageId>).+(?=</PackageId>)");
                packageName = match.Success ? match.Value : string.Empty;
            }

            return packageName;
        }

        /// <summary>
        /// 替换本地引用为Nuget引用
        /// </summary>
        public void SwitchReferences()
        {
            var toBeAddPackageNames = new List<string>();

            foreach (var referenceFileInfo in LocalReferenceList)
            {
                var packageName = GetPackageName(referenceFileInfo);
                if (!string.IsNullOrWhiteSpace(packageName))
                {
                    Console.WriteLine($"remove {referenceFileInfo.FullName} from {FileInfo.FullName}");

                    //移除之前的引用，添加新引用
                    DotnetHelper.RemoveLocalReference(FileInfo, referenceFileInfo);
                    toBeAddPackageNames.Add(packageName);
                }
            }

            foreach (var toBeAddPackageName in toBeAddPackageNames)
            {
                Console.WriteLine($"add package {toBeAddPackageName} to {FileInfo.FullName}");
                DotnetHelper.AddNugetReference(FileInfo, toBeAddPackageName);
            }
        }
    }
}
