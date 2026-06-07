using System.Windows;

namespace ImperialWorkbench;

/// <summary>
/// Optional native WPF entry point. The Python GUI remains the primary surface;
/// this exists for operators who want a compiled, GPU-accelerated native skin.
/// </summary>
public partial class App : Application
{
}
