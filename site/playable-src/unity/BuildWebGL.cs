using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;

public static class JuneJamWebGLBuilder
{
    private static bool allowSampleScene;

    public static void Build()
    {
        var outputPath = GetArg("-customBuildPath");
        if (string.IsNullOrWhiteSpace(outputPath))
        {
            throw new ArgumentException("Missing -customBuildPath");
        }

        Directory.CreateDirectory(outputPath);
        allowSampleScene = ProjectReferencesSampleScene();

        var scenes = EditorBuildSettings.scenes
            .Where(scene => scene.enabled)
            .Select(scene => scene.path)
            .Where(IsRealScene)
            .ToArray();

        if (scenes.Length == 1 && IsSampleScene(scenes[0]) && allowSampleScene)
        {
            scenes = Array.Empty<string>();
        }

        if (scenes.Length == 0)
        {
            scenes = AssetDatabase.FindAssets("t:Scene")
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(IsRealScene)
                .OrderBy(SceneSortKey)
                .ToArray();
        }

        if (scenes.Length == 0)
        {
            throw new InvalidOperationException("No Unity scenes found to build.");
        }

        Console.WriteLine("Building scenes:");
        foreach (var scene in scenes)
        {
            Console.WriteLine(scene);
        }

        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.decompressionFallback = true;
        PlayerSettings.WebGL.threadsSupport = false;

        var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = outputPath,
            target = BuildTarget.WebGL,
            options = BuildOptions.None,
        });

        if (report.summary.result != BuildResult.Succeeded)
        {
            throw new InvalidOperationException($"WebGL build failed: {report.summary.result}");
        }
    }

    private static string SceneSortKey(string path)
    {
        var file = Path.GetFileNameWithoutExtension(path).ToLowerInvariant();
        if (file == "start page" || file == "startpage" || file == "main menu" || file == "mainmenu" || file == "main_menu" || file == "menu")
        {
            return "000_" + path;
        }

        if (file == "samplescene")
        {
            return "010_" + path;
        }

        return "100_" + path;
    }

    private static bool IsRealScene(string path)
    {
        return !string.IsNullOrWhiteSpace(path)
            && path.EndsWith(".unity", StringComparison.OrdinalIgnoreCase)
            && (allowSampleScene || !IsSampleScene(path))
            && !path.StartsWith("Packages/", StringComparison.OrdinalIgnoreCase)
            && !path.Contains("SceneTemplate", StringComparison.OrdinalIgnoreCase)
            && !path.Contains("/Demo/", StringComparison.OrdinalIgnoreCase)
            && !path.Contains("/Examples", StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsSampleScene(string path)
    {
        return path.Contains("/SampleScene.unity", StringComparison.OrdinalIgnoreCase);
    }

    private static bool ProjectReferencesSampleScene()
    {
        return AssetDatabase.FindAssets("t:MonoScript")
            .Select(AssetDatabase.GUIDToAssetPath)
            .Where(path => path.EndsWith(".cs", StringComparison.OrdinalIgnoreCase))
            .Any(path => File.ReadAllText(path).Contains("\"SampleScene\"", StringComparison.Ordinal));
    }

    private static string GetArg(string name)
    {
        var args = Environment.GetCommandLineArgs();
        for (var i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == name)
            {
                return args[i + 1];
            }
        }

        return null;
    }
}
