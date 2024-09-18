package com.bandbridge.audio;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

import java.io.File;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.stream.Stream;

import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.fail;

public class AudioUnitTest {

    String audioPath = "assets/";

    @BeforeAll
    public static void setup() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = 6000;
    }

    private static Stream<TestData> songProvider() {
        return Stream.of(
                new TestData("assets/getback.mp3", 124, "A", "minor"), // 123.7772
                new TestData("assets/adoreyou.mp3", 99, "C", "minor"), // 99
                new TestData("assets/believe.mp3", 79, "A", "mixolydian"), // 79
                new TestData("assets/blindinglights.m4a", 87, "F", "mixolydian"), // 85
                new TestData("assets/boydoesnothing.mp3", 174, "D#", "mixolydian"), // 174
                new TestData("assets/children.mp3", 140, "F", "minor"), // 140
                new TestData("assets/crazyinlove.mp3", 100, "F", "minor"), // 100
                new TestData("assets/dontyouforgetaboutme.mp3", 114, "E", "minor"), // 114
                new TestData("assets/easysilence.mp3", 87, "D", "major"),
                new TestData("assets/itouchmyself.mp3", 110, "C", "mixolydian"));
    }

    @ParameterizedTest
    @MethodSource("songProvider")
    void testTempoEndpoint(TestData testData) {
        File mp3File = getResourceFile(testData.songPath);
        Response response = given()
                .multiPart("file", mp3File)
                .when()
                .post("/librosa/tempo")
                .then()
                .statusCode(200)
                .extract()
                .response();

        float tempo = response.jsonPath().getFloat("tempo");
        String message = String.format("Tempo of %s should be %s", testData.songPath, testData.expectedTempo);
        assertEquals(testData.expectedTempo, tempo, message);
    }

    @ParameterizedTest
    @MethodSource("songProvider")
    void testKeyEndpoint(TestData testData) {
        File mp3File = getResourceFile(testData.songPath);
        Response response = given()
                .multiPart("file", mp3File)
                .when()
                .post("/librosa/key")
                .then()
                .statusCode(200)
                .extract()
                .response();

        String key = response.jsonPath().getString("key");
        String mode = response.jsonPath().getString("mode");
        String keyMessage = String.format("Key of %s should be %s", testData.songPath, testData.expectedKey);
        assertEquals(testData.expectedKey, key, keyMessage);
        String modeMessage = String.format("Mode of %s should be %s", testData.songPath, testData.expectedMode);
        assertEquals(testData.expectedMode, mode, modeMessage);
    }

    private File getResourceFile(String relativePath) {
        URL resourceUrl = getClass().getClassLoader().getResource(relativePath);
        assertNotNull(resourceUrl, "Resource not found: " + relativePath);
        try {
            return new File(resourceUrl.toURI());
        } catch (URISyntaxException e) {
            fail("Invalid URI syntax for resource: " + relativePath);
            return null; // Unreachable, but required by the compiler
        }
    }

    private static class TestData {
        String songPath;
        float expectedTempo;
        String expectedKey;
        String expectedMode;

        TestData(String songPath, float expectedTempo, String expectedKey, String expectedMode) {
            this.songPath = songPath;
            this.expectedTempo = expectedTempo;
            this.expectedKey = expectedKey;
            this.expectedMode = expectedMode;
        }
    }
}