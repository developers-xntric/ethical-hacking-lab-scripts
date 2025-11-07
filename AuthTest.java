// Simple authorization header tester.
// WARNING: Use only on systems you own or have explicit permission to test.

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;

public class AuthTest {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java AuthTest <target_url>");
            System.exit(2);
        }

        String target = args[0];
        List<String> authPayloads = List.of(
            "Basic admin:password",
            "' OR 1=1--"
        );

        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build();

        boolean vulnerable = false;

        System.out.println("Testing authorization at " + target);

        for (String payload : authPayloads) {
            try {
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(target))
                        .timeout(Duration.ofSeconds(10))
                        .header("Authorization", payload)
                        .GET()
                        .build();

                HttpResponse<String> resp = client.send(request, HttpResponse.BodyHandlers.ofString());
                int status = resp.statusCode();
                String bodyLower = resp.body() == null ? "" : resp.body().toLowerCase();

                System.out.printf("Payload: %s  -> status: %d, body-length: %d%n", payload, status, resp.body() == null ? 0 : resp.body().length());

                if (status == 200 || bodyLower.contains("success")) {
                    System.out.println("[POSSIBLE VULN] Authorization accepted with payload: " + payload);
                    vulnerable = true;
                } else {
                    System.out.println("Not accepted.");
                }
            } catch (Exception e) {
                System.out.println("Error with payload [" + payload + "]: " + e.getMessage());
            }
        }

        if (vulnerable) {
            System.out.println("\n[VULNERABLE] Authorization mechanisms may be flawed!");
        } else {
            System.out.println("\nAuthorization appears secure (no obvious bypass detected).");
        }
    }
}
