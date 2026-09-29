using System.Runtime.InteropServices;

namespace AdsApp
{
    [StructLayout(LayoutKind.Sequential, Pack = 1)]
    public struct ST_SensorData
    {
        [MarshalAs(UnmanagedType.I1)]
        public bool bActive;
        public short nId;
        public float fValue;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 81)]
        public string sName;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 5)]
        public short[] aValues;
    }
}