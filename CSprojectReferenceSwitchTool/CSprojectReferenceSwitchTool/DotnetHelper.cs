using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

namespace CSprojectReferenceSwitchTool
{
    public class DotnetHelper
    {
        /// <summary>
        /// 获取本地程序集的引用
        /// </summary>
        /// <param name="csprojectFileInfo"></param>
        /// <returns></returns>
        public static List<FileInfo> GetLocalReferenceList(FileInfo csprojectFileInfo)
        {
            if (csprojectFileInfo == null)
            {
                throw new ArgumentNullException(nameof(csprojectFileInfo));
            }

            var parms = $"list \"{csprojectFileInfo.FullName}\" reference";
            var references = RunDotnet(parms).Split(Environment.NewLine);

            var result = new List<FileInfo>();

            if (references.Length > 2)
            {
                //有项目引用
                for (int i = 2; i < references.Length; i++)
                {
                    var absoultFullPath = Path.GetFullPath(references[i], csprojectFileInfo.DirectoryName);
                    var fileInfo = new FileInfo(absoultFullPath);

                    if (fileInfo.Exists)
                    {
                        result.Add(fileInfo);
                    }
                }
            }

            return result;
        }

        /// <summary>
        /// 移除本地程序集的相对引用
        /// </summary>
        /// <param name="csprojectFileInfo"></param>
        /// <param name="referenceFileInfo"></param>
        public static void RemoveLocalReference(FileInfo csprojectFileInfo, FileInfo referenceFileInfo)
        {
            if (csprojectFileInfo == null)
            {
                throw new ArgumentNullException(nameof(csprojectFileInfo));
            }

            if(referenceFileInfo == null)
            {
                throw new ArgumentNullException(nameof(referenceFileInfo));
            }

            var parms = $"remove \"{csprojectFileInfo.FullName}\" reference \"{referenceFileInfo.FullName}\"";
            RunDotnet(parms);
        }

        /// <summary>
        /// 添加引用
        /// </summary>
        /// <param name="csprojectFileInfo"></param>
        /// <param name="packageName"></param>
        public static void AddNugetReference(FileInfo csprojectFileInfo, string packageName)
        {
            if (csprojectFileInfo == null)
            {
                throw new ArgumentNullException(nameof(csprojectFileInfo));
            }

            var parms = $"add \"{csprojectFileInfo.FullName}\" package \"{packageName}\"";
            var s = RunDotnet(parms);
        }

        /// <summary>
        /// 运行Dotnet命令
        /// </summary>
        /// <param name="parms">参数</param>
        /// <returns></returns>
        private static string RunDotnet(string parms)
        {
            var result = string.Empty;
            var dotnetRunner = new Process {StartInfo = new ProcessStartInfo("dotnet", parms) {RedirectStandardOutput = true}};

            if (dotnetRunner.Start())
            {
                result = dotnetRunner.StandardOutput.ReadToEnd();
                dotnetRunner.WaitForExit();
            }

            return result;
        }
    }
}
