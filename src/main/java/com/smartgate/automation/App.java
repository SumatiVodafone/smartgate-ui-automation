package com.smartgate.automation;

import java.io.InputStream;
import java.net.URL;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.bonigarcia.wdm.WebDriverManager;

public class App {

    private static final Path PROJECT_ROOT = Paths.get("").toAbsolutePath();
    private static final Path DOWNLOAD_ROOT = PROJECT_ROOT.getParent().resolve("smartgate-downloads");
    private static final Path DEFAULT_CHROME_USER_DATA_DIR = Paths.get(
            System.getenv("LOCALAPPDATA"),
            "Smartgate",
            "Chrome User Data"
    );

    private static final String DEVICE_INFORMATION_URL
            = "https://raw.githubusercontent.com/"
            + "VFTV-Testing/Configs/Main/"
            + "AVSB_GEN3_Configs/deviceInformation.json";


    /* =========================================================
       DASHBOARD URLS
       ========================================================= */
    private static final String CT_LONGPLAYBACK_BASE_URL
            = "https://vodafonevcoe.cloud.witbe.net/smartgate/d/TYM0n1z7q/service-identity-card"
            + "?orgId=1"
            + "&from-dash=WAtJX5fVz"
            + "&from=now-30d"
            + "&to=now"
            + "&var-category=CT"
            + "&var-category=LongPlayback"
            + "&var-service=All"
            + "&var-feature=All"
            + "&var-releaseVersion=All"
            + "&var-experience=All"
            + "&var-groupBy=undefined"
            + "&var-KPI=serviceAvailability"
            + "&var-environmentVersion=All"
            + "&var-deviceName=All"
            + "&var-resourceVersionType=production"
            + "&var-groupByFilter=qa.platform,qa.releaseVersion,qa.service,qa.category,qa.feature,qa.environmentVersion";

    private static final String ZAPPING_URL
            = "https://vodafonevcoe.cloud.witbe.net/smartgate/d/NUtCppuMz/channel-detailed-tests-on-experience-table"
            + "?orgId=1"
            + "&from-dash=6sKfCdXGz"
            + "&from=now-2d"
            + "&to=now"
            + "&var-platform=All"
            + "&var-experience=All"
            + "&var-region=All"
            + "&var-cityName=All"
            + "&var-deviceName=All"
            + "&var-channelName=All"
            + "&var-groupBy=channelName"
            + "&var-feedbackStastusList=All"
            + "&var-serviceProductionStatus=All"
            + "&var-resourceVersionType=production"
            + "&var-maestroUuid=06af0c4d-eae6-4f49-ab72-8d50b134bd18"
            + "&var-integrity=All"
            + "&var-errorPieChart=5"
            + "&var-errorLabel=All";

    private static final String ENV_DEVICE_BASE_URL
            = "https://vodafonevcoe.cloud.witbe.net/smartgate/d/QacOvereSVz/service-overview-table"
            + "?orgId=1"
            + "&from-dash=WAtJX5fVz"
            + "&from=now-24h"
            + "&to=now"
            + "&var-category=CT"
            + "&var-category=Maintenance"
            + "&var-category=LongPlayback"
            + "&var-service=All"
            + "&var-feature=All"
            + "&var-experience=All"
            + "&var-releaseVersion=All"
            + "&var-environmentVersion=All"
            + "&var-deviceName=All"
            + "&var-serviceProductionStatus=Production"
            + "&var-resourceVersionType=production"
            + "&var-errorPieChart=5"
            + "&var-errorLabel=All";

    /* =========================================================
   LOAD HARDWARE PLATFORMS FROM GITHUB
   ========================================================= */
    private static Set<String> getHardwarePlatforms() throws Exception {

        Set<String> hardwarePlatforms = new TreeSet<>();

        ObjectMapper mapper = new ObjectMapper();

        try (InputStream inputStream = new URL(DEVICE_INFORMATION_URL).openStream()) {

            JsonNode root = mapper.readTree(inputStream);

            root.fields().forEachRemaining(entry -> {

                JsonNode device = entry.getValue();

                JsonNode hardware = device.get("Hardware");

                if (hardware != null && !hardware.asText().isBlank()) {
                    hardwarePlatforms.add(hardware.asText().trim());
                }
            });
        }

        System.out.println("Hardware platforms loaded from GitHub:");
        hardwarePlatforms.forEach(System.out::println);

        return hardwarePlatforms;
    }

    /* =========================================================
   APPEND HARDWARE PLATFORMS TO DASHBOARD URL
   ========================================================= */
    private static String appendPlatforms(String baseUrl) throws Exception {

        StringBuilder url = new StringBuilder(baseUrl);

        Set<String> hardwarePlatforms = getHardwarePlatforms();
        System.out.println("Adding " + hardwarePlatforms.size() + " hardware platforms to URL...");

        for (String platform : hardwarePlatforms) {
            url.append("&var-platform=").append(platform);
        }

        return url.toString();
    }

    public static void main(String[] args) throws Exception {

        /* =========================================================
           SETUP CHROMEDRIVER
           ========================================================= */
        WebDriverManager.chromedriver().setup();

        /* =========================================================
           DASHBOARD TYPE FROM PYTHON
           ========================================================= */
        String dashboardType = "CT";

        if (args.length > 0) {
            dashboardType = args[0];
        }

        Path downloadDir;
        String selectedUrl;

        /* =========================================================
           ROUTING LOGIC
           ========================================================= */
        if (dashboardType.equalsIgnoreCase("Zapping")) {

            downloadDir = DOWNLOAD_ROOT.resolve("Zapping");
            selectedUrl = ZAPPING_URL;

        } else if (
                dashboardType.equalsIgnoreCase("Maintenance")
                || dashboardType.equalsIgnoreCase("Devices Without Test Execution")
                || dashboardType.equalsIgnoreCase("DeviceNoExecution")) {

            downloadDir = DOWNLOAD_ROOT.resolve("Maintenance-DeviceNoExecution");
            selectedUrl = appendPlatforms(ENV_DEVICE_BASE_URL);

        } else {

            downloadDir = DOWNLOAD_ROOT.resolve("CT-LongPlayback");
            selectedUrl = appendPlatforms(CT_LONGPLAYBACK_BASE_URL);
        }

        Files.createDirectories(downloadDir);

        /* =========================================================
           CHROME DOWNLOAD PREFS
           ========================================================= */
        Map<String, Object> prefs = new HashMap<>();
        prefs.put("download.default_directory", downloadDir.toString());
        prefs.put("download.prompt_for_download", false);
        prefs.put("download.directory_upgrade", true);
        prefs.put("safebrowsing.enabled", true);

        ChromeOptions options = new ChromeOptions();

        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--disable-gpu");
        options.addArguments("--remote-allow-origins=*");
        options.addArguments("--start-maximized");

        /* =========================================================
           PERSIST LOGIN SESSION
           ========================================================= */
        String chromeUserDataDir = System.getenv().getOrDefault(
                "SMARTGATE_CHROME_USER_DATA_DIR",
                DEFAULT_CHROME_USER_DATA_DIR.toString()
        );
        String chromeProfileName = System.getenv().getOrDefault(
                "SMARTGATE_CHROME_PROFILE_NAME",
                "Default"
        );

        options.addArguments("--user-data-dir=" + Paths.get(chromeUserDataDir).toAbsolutePath());
        options.addArguments("--profile-directory=" + chromeProfileName);
        options.setExperimentalOption("prefs", prefs);

        WebDriver driver = new ChromeDriver(options);

        try {

            /* =========================================================
               OPEN DASHBOARD
               ========================================================= */
            driver.get("about:blank");
            driver.navigate().to(selectedUrl);

            System.out.println("Dashboard selected: " + dashboardType);
            System.out.println("Download folder: " + downloadDir);
            System.out.println("Opened URL: " + selectedUrl);

            Thread.sleep(7000);

            /* =========================================================
               WAIT FOR CSV EXPORT BUTTON
               ========================================================= */
            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(60));

            WebElement csvBtn = wait.until(
                    ExpectedConditions.elementToBeClickable(
                            By.xpath("//span[normalize-space()='CSV Export']")
                    )
            );

            long beforeDownload = System.currentTimeMillis();

            ((JavascriptExecutor) driver)
                    .executeScript("arguments[0].click();", csvBtn);

            /* =========================================================
               WAIT FOR DOWNLOAD
               ========================================================= */
            waitForCsv(downloadDir, 60, beforeDownload);

            System.out.println("CSV downloaded successfully");

        } finally {
            driver.quit();
        }
    }

    /* =========================================================
       WAIT FOR NEW CSV FILE
       ========================================================= */
    private static void waitForCsv(Path dir, int timeoutSec, long beforeTime) throws Exception {

        long end = System.currentTimeMillis() + timeoutSec * 1000L;

        while (System.currentTimeMillis() < end) {

            try (DirectoryStream<Path> files = Files.newDirectoryStream(dir, "*.csv")) {

                for (Path f : files) {

                    long modified = Files.getLastModifiedTime(f).toMillis();

                    if (modified > beforeTime) {
                        System.out.println("Downloaded: " + f.getFileName());
                        return;
                    }
                }
            }

            Thread.sleep(1000);
        }

        throw new RuntimeException("CSV download timeout");
    }
}