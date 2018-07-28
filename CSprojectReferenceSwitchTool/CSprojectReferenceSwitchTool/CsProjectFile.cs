using System.IO;

namespace CSprojectReferenceSwitchTool
{
    public class CsProjectFile
    {
        public FileInfo FileInfo { get; private set; }

        public CsProjectFile(FileInfo fileInfo)
        {
            FileInfo = fileInfo;
        }
    }
}
