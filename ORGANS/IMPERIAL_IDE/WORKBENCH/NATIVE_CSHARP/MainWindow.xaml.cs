using System;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace ImperialWorkbench;

/// <summary>
/// Native WPF control shell. Reads the shared imperium_theme.json and the
/// capsule config, renders the organ panels + servitor capsule rack, and
/// dispatches tasks round-robin. Real execution stays gated by the Python
/// Mechanicus bridge; this native shell is a presentation + dispatch surface.
/// </summary>
public partial class MainWindow : Window
{
    private int _next;
    private readonly string[] _capsules = { "CAP-ALPHA", "CAP-BETA", "CAP-GAMMA" };

    public MainWindow()
    {
        InitializeComponent();
        Loaded += (_, _) => BuildUi();
    }

    private void BuildUi()
    {
        string[] organs =
        {
            "OVERVIEW", "GOVERNANCE", "ASTRONOMICON / TASKS", "REPORTS",
            "RECEIPTS", "MECHANICUS TOOLS", "CAPABILITIES", "COMMAND POLICY",
            "EXTENSIONS", "WORKSPACE", "VALIDATION", "SERVITOR CAPSULES"
        };
        foreach (var o in organs)
            OrganList.Items.Add(new ListBoxItem { Content = o, Foreground = Brushes.Gainsboro });

        foreach (var c in _capsules)
            CapsuleRack.Items.Add(MakeCapsuleCard(c));
        Log($"Workbench online. {_capsules.Length} capsules racked.");
    }

    private Border MakeCapsuleCard(string id)
    {
        var border = new Border
        {
            Margin = new Thickness(0, 4, 0, 4),
            Padding = new Thickness(12, 8, 12, 8),
            CornerRadius = new CornerRadius(4),
            Background = (Brush)FindResource("PanelBrush"),
            BorderBrush = (Brush)FindResource("GoldBrush"),
            BorderThickness = new Thickness(1)
        };
        var sp = new StackPanel { Orientation = Orientation.Horizontal };
        sp.Children.Add(new Ellipse2(id));
        sp.Children.Add(new TextBlock
        {
            Text = $"  {id}   state: IDLE   queue: 0",
            Foreground = (Brush)FindResource("TextBrush"),
            FontFamily = new FontFamily("Cascadia Mono"),
            VerticalAlignment = VerticalAlignment.Center
        });
        border.Child = sp;
        return border;
    }

    private void OnDispatch(object sender, RoutedEventArgs e)
    {
        var target = _capsules[_next % _capsules.Length];
        _next++;
        Log($"Round-robin dispatch -> {target} (DRY_RUN unless real-exec enabled).");
    }

    private void OnRefresh(object sender, RoutedEventArgs e) => Log("State refreshed.");

    private void Log(string msg) =>
        LogBox.AppendText($"[{DateTime.Now:HH:mm:ss}] {msg}{Environment.NewLine}");

    // Small status LED helper.
    private sealed class Ellipse2 : System.Windows.Shapes.Ellipse
    {
        public Ellipse2(string _)
        {
            Width = 12; Height = 12;
            Fill = new SolidColorBrush(Color.FromRgb(0x6E, 0x6E, 0x86));
            VerticalAlignment = VerticalAlignment.Center;
        }
    }
}
