package com.smartgate.automation;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.nio.file.*;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

public class App {

    /* =========================================================
       DASHBOARD URLS
       ========================================================= */

    private static final String CT_LONGPLAYBACK_URL =
        "https://vodafonevcoe.cloud.witbe.net/smartgate/d/TYM0n1z7q/service-identity-card"
            + "?orgId=1"
            + "&from-dash=WAtJX5fVz"
            + "&from=now-30d"
            + "&to=now"
            + "&var-category=CT"
            + "&var-category=LongPlayback"
            + "&var-service=All"
            + "&var-feature=All"
            + "&var-releaseVersion=All"
            + "&var-platform=AVSB"
            + "&var-platform=GEN3"
            + "&var-platform=GEN4_SGM"
            + "&var-experience=All"
            + "&var-groupBy=undefined"
            + "&var-KPI=serviceAvailability"
            + "&var-environmentVersion=All"
            + "&var-deviceName=All"
            + "&var-resourceVersionType=production"
            + "&var-groupByFilter=qa.platform,qa.releaseVersion,qa.service,qa.category,qa.feature,qa.environmentVersion";

    private static final String ZAPPING_URL =
        "https://vodafonevcoe.cloud.witbe.net/smartgate/d/6sKfCdXGz/kpis-stats-table"
            + "?orgId=1"
            + "&var-platform=All"
            + "&var-experience=All"
            + "&var-region=All"
            + "&var-cityName=All"
            + "&var-deviceName=All"
            + "&var-channelName=All"
            + "&var-groupBy=experience"
            + "&var-serviceProductionStatus=Production"
            + "&var-resourceVersionType=production"
            + "&var-integrity=No"
            + "&var-errorPieChart=5"
            + "&from=now-30d"
            + "&to=now";

    private static final String ENV_DEVICE_URL =
        "https://vodafonevcoe.cloud.witbe.net/smartgate/d/QacOvereSVz/service-overview-table"
            + "?orgId=1"
            + "&from-dash=WAtJX5fVz"
            + "&from=now-24h"
            + "&to=now"
            + "&var-category=CT"
            + "&var-category=Environmental"
            + "&var-category=LongPlayback"
            + "&var-service=All"
            + "&var-feature=All"
            + "&var-platform=AVSB"
            + "&var-platform=GEN3"
            + "&var-platform=GEN4_SGM"
            + "&var-experience=All"
            + "&var-releaseVersion=All"
            + "&var-environmentVersion=All"
            + "&var-deviceName=All"
            + "&var-serviceProductionStatus=Production"
            + "&var-resourceVersionType=production"
            + "&var-errorPieChart=5"
            + "&var-errorLabel=All";

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

            downloadDir = Paths.get("C:\\projects\\smartgate-downloads\\Zapping");
            selectedUrl = ZAPPING_URL;

        } else if (
            dashboardType.equalsIgnoreCase("Environmental")
            || dashboardType.equalsIgnoreCase("Devices Without Test Execution")
            || dashboardType.equalsIgnoreCase("DeviceNoExecution")
        ) {

            downloadDir = Paths.get("C:\\projects\\smartgate-downloads\\Environmental-DeviceNoExecution");
            selectedUrl = ENV_DEVICE_URL;

        } else {

            // CT + LongPlayback
            downloadDir = Paths.get("C:\\projects\\smartgate-downloads\\CT-LongPlayback");
            selectedUrl = CT_LONGPLAYBACK_URL;
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
        Path profileDir = Paths.get("C:\\selenium-profile").toAbsolutePath();
        Files.createDirectories(profileDir);

        options.addArguments("--user-data-dir=" + profileDir.toString());
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