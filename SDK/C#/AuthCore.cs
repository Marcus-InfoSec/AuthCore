using Newtonsoft.Json;
using NSec.Cryptography;
using System.Net.Security;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Security.Principal;
using System.Text;
using PublicKey = NSec.Cryptography.PublicKey;


public static class AuthCore
{
    public class AuthResponse
    {
        public string status { get; set; }
        public string message { get; set; }
        public string hwid { get; set; }
        public string license_key { get; set; }
        public DateTime expires_at { get; set; }
    }
    private const string publicKey = "changeme";
    private static readonly HashSet<string> certHash = new()
{
    "changeme"
};
    private static bool VerifyEd25519Signature(
     string publicKeyBase64,
     string message,
     string signatureBase64)
    {
        try
        {
            byte[] publicKeyBytes = Convert.FromBase64String(publicKeyBase64);
            byte[] messageBytes = Encoding.UTF8.GetBytes(message);
            byte[] signatureBytes = Convert.FromBase64String(signatureBase64);

            if (publicKeyBytes.Length != 32 || signatureBytes.Length != 64)
                return false;

            var algorithm = SignatureAlgorithm.Ed25519;

            var publicKey = PublicKey.Import(algorithm, publicKeyBytes, KeyBlobFormat.RawPublicKey);

            return algorithm.Verify(publicKey, messageBytes, signatureBytes);
        }
        catch
        {
            return false;
        }
    }

    private static HttpClient CreatePinnedClient()
    {
        var handler = new HttpClientHandler();

        handler.ServerCertificateCustomValidationCallback =
    (req, cert, chain, errors) =>
    {
        if (cert == null)
            return false;

        using var ecdsa = cert.GetECDsaPublicKey();
        if (ecdsa == null)
            return false;

        byte[] spkiDer = ecdsa.ExportSubjectPublicKeyInfo();

        using var sha256 = SHA256.Create();
        string spki = Convert.ToBase64String(
            sha256.ComputeHash(spkiDer)
        );

#if DEBUG
        Console.WriteLine("[TLS] SPKI(server): " + spki);
        Console.WriteLine("[TLS] Errors: " + errors);
#endif

        return certHash.Contains(spki);
    };

        return new HttpClient(handler)
        {
            Timeout = TimeSpan.FromSeconds(10)
        };
    }
    
    public static bool Authorize(string licenseKey, string hwid, string serverBaseUrl, out AuthResponse result)
    {
        result = null;

        try
        {
            using (var client = CreatePinnedClient())
            {
                var payload = new
                {
                    license_key = licenseKey,
                    hwid = hwid
                };

                string json = JsonConvert.SerializeObject(payload);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = client.PostAsync(
                    serverBaseUrl.TrimEnd('/') + "/auth",
                    content
                ).GetAwaiter().GetResult();

                string responseText = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();

                string signature = response.Headers.TryGetValues("x-signature-ed25519", out var sig)
                    ? sig.FirstOrDefault()
                    : null;

                string timestamp = response.Headers.TryGetValues("x-signature-timestamp", out var ts)
                    ? ts.FirstOrDefault()
                    : null;

                if (string.IsNullOrEmpty(signature) || string.IsNullOrEmpty(timestamp))
                {
                    result = new AuthResponse
                    {
                        status = "error",
                        message = "Missing signature headers"
                    };
                    return false;
                }

                string message = timestamp + responseText;

                if (!VerifyEd25519Signature(publicKey, message, signature))
                {
                    result = new AuthResponse
                    {
                        status = "error",
                        message = "Signature verification failed"
                    };
                    return false;
                }

                long serverTs = long.Parse(timestamp);
                long nowTs = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

                if (Math.Abs(nowTs - serverTs) > 20)
                {
                    result = new AuthResponse
                    {
                        status = "error",
                        message = "Please synchronize your device."
                    };
                    return false;
                }

                result = JsonConvert.DeserializeObject<AuthResponse>(responseText);
                return result != null && result.status == "success";
            }
        }
        catch (Exception ex)
        {
            result = new AuthResponse
            {
                status = "error",
                message = $"Exception: {ex.Message}"
            };
            return false;
        }
    }

    public static string GetHWID()
    {
        return WindowsIdentity.GetCurrent().User.Value;
    }
}
