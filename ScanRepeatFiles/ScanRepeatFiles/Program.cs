using FrHello.NetLib.Core.Security;

namespace ScanRepeatFiles
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            var fileNameDic = new Dictionary<string, List<string>>();
            var md5Dic = new Dictionary<string, List<string>>();

            var dir = @"C:\Users\fengr\OneDrive";
            var files = Directory.GetFiles(dir, "*.*", SearchOption.AllDirectories);
            foreach (var file in files)
            {
                try
                {
                    await using var stream = File.OpenRead(file);
                    var md5 = await SecurityHelper.Hash.Md5.ComputeHashFast(stream);

                    var fileName = Path.GetFileName(file);
                    if (md5Dic.ContainsKey(md5))
                    {
                        md5Dic[md5].Add(fileName);
                    }
                    else
                    {
                        md5Dic.Add(md5, new List<string> { fileName });
                    }

                    if (fileNameDic.ContainsKey(fileName))
                    {
                        fileNameDic[fileName].Add(fileName);
                    }
                    else
                    {
                        fileNameDic.Add(fileName, new List<string> { fileName });
                    }
                }
                catch
                {
                    Console.WriteLine(file + "  读取异常");
                }
            }

            Console.WriteLine("文件名重复：");
            foreach (var item in fileNameDic)
            {
                if (item.Value.Count > 1)
                {
                    Console.WriteLine(string.Join("---", item.Value));
                }
            }

            Console.WriteLine();
            Console.WriteLine("Md5 重复：");
            foreach (var item in md5Dic)
            {
                if (item.Value.Count > 1)
                {
                    Console.WriteLine(string.Join("---", item.Value));
                }
            }

            Console.WriteLine("Hello, World!");
        }
    }
}