// See https://aka.ms/new-console-template for more information

using System.Diagnostics;
using System.Text.RegularExpressions;

Console.WriteLine("开始查找");
var sw = Stopwatch.StartNew();

var files = Directory.GetFiles(Directory.GetCurrentDirectory(), "*", SearchOption.AllDirectories);

var regex = new Regex(@".*(\(\s*\d+\s*\)|（\s*\d+\s*）)\.");
Parallel.ForEach(files, file =>
{
    if (regex.IsMatch(file))
    {
        Console.WriteLine(file);
    }
});

sw.Stop();
Console.WriteLine("查找结束，耗时：{0}", sw.ElapsedMilliseconds);

Console.ReadLine();
