package com.bandbridge.audio;

import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.File;

import static io.restassured.RestAssured.given;
import static org.junit.jupiter.api.Assertions.assertTrue;


public class AudioUnitTest {

    @BeforeAll
    public static void setup() {
        RestAssured.baseURI = "http://localhost";
        RestAssured.port = 6000;
    }

    @Test
    public void testTempoEndpoint() {
        String filePath = "/path/to/getback.mp3";
        Response response = given()
                .multiPart("file", new File(filePath))
                .when()
                .post("/librosa/tempo")
                .then()
                .statusCode(200)
                .extract()
                .response();

        float tempo = response.jsonPath().getFloat("tempo");
        assertTrue(tempo > 0, "Tempo should be greater than 0");
    }

    @Test
    public void testKeyEndpoint() {
        String filePath = "/path/to/getback.mp3";
        Response response = given()
                .multiPart("file", new File(filePath))
                .when()
                .post("/librosa/key")
                .then()
                .statusCode(200)
                .extract()
                .response();

        String key = response.jsonPath().getString("key");
        String mode = response.jsonPath().getString("mode");
        assertTrue(key.matches("[A-G]#?"), "Key should be a valid musical key");
        assertTrue(mode.matches("major|minor|mixolydian"), "Mode should be major, minor, or mixolydian");
    }
}