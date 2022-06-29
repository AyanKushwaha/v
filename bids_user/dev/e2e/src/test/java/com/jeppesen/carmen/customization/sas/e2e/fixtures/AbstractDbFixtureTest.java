package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.E2eApplication;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import static org.springframework.boot.test.context.SpringBootTest.WebEnvironment.NONE;

@Tag("DBF")
@ActiveProfiles("db-fixtures")
@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = E2eApplication.class, webEnvironment = NONE)
public abstract class AbstractDbFixtureTest {
}
