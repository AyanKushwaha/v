package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import com.codeborne.selenide.Selenide;
import io.vavr.control.Try;
import lombok.extern.log4j.Log4j2;
import org.openqa.selenium.By;

import java.io.*;

import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.WebDriverRunner.closeWebDriver;
import static java.lang.Integer.min;
import static java.lang.String.format;
import static java.lang.Thread.sleep;
import static org.apache.commons.io.FileUtils.deleteDirectory;
import static org.apache.commons.io.FileUtils.forceMkdir;

/**
 * The class solves connection issues to Selenium grid.
 * It tries to connect with Selenide.open(url) method several times.
 * Connection is successfully established if the page marker is present on requested login page.
 * Sometimes Selenium grid returns wrong page. It will be logged to a separate file.
 */
@Log4j2
public class SeleniumGridAdapter {
    private static final String PAGE_MARKER = "c_username";
    private static final int MAX_RETRIES = 10;
    private static final int PAUSE_TO_RETRY = 5000;

    public static void open(String url) {
        int counter = 0;
        while (!connectTo(url) && ++counter <= MAX_RETRIES) {
            close();
            Try.run(() -> sleep(PAUSE_TO_RETRY)).onFailure(e -> log.info("Interrupted: {}", e.getLocalizedMessage()));
        }

        if (counter > 0) {
            log.info("Connection retries for {}: {}", url, min(counter, MAX_RETRIES));
            if (counter > MAX_RETRIES) log.error("Connection to Selenium grid wasn't established.");
        }
    }

    private static boolean connectTo(String url) {
        try {
            Selenide.open(url);
        } catch (Exception ex) {
            log.error("Connection issues: {}\n", ex.getMessage());
            return false;
        }
        return hasLoginPage(url);
    }

    private static boolean hasLoginPage(String url) {
        String page = $(By.tagName("body")).innerHtml();
        boolean isLoginPage = page.contains(PAGE_MARKER);
        if (!isLoginPage) {
            log.info("Requested page is not found: {}", url);
            writePageLog(page, url);
        }
        return isLoginPage;
    }

    private static void writePageLog(String page, String url) {
        File logDir = new File("./logs");
        try {
            if (logDir.exists()) deleteDirectory(logDir);
            forceMkdir(logDir);
        } catch (IOException e) {
            log.error("Unable to delete/create directory {}", logDir.getPath());
            return;
        }

        String logFilePath = logDir.getPath() + "/LoginPage.log";
        File logFile = new File(logFilePath);
        try (OutputStream outputStream = new FileOutputStream(logFile)) {
            byte[] content = (format("URL: %s%n\r%s", url, page)).getBytes();
            outputStream.write(content);
            log.info("Page log for {} has been saved: {}", url, logFile.getAbsolutePath());
        } catch (FileNotFoundException e) {
            log.error("unable to find file {}: {}", logFile.getAbsolutePath(), e.getMessage());
        } catch (IOException e) {
            log.error("unable to save file {}: {}", logFile.getAbsolutePath(), e.getMessage());
        }
    }

    public static void close() {
        close(MAX_RETRIES);
    }

    private static void close(int maxRetries) {
        try {
            closeWebDriver();
        } catch (Exception ex) {
            log.error("Connection wasn't closed, left {} retries: {}\n", maxRetries, ex.getMessage());
            if (maxRetries > 0) close(--maxRetries);
        }
    }

    private SeleniumGridAdapter() {
    }
}
