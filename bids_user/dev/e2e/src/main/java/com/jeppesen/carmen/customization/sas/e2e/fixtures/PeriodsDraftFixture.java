package com.jeppesen.carmen.customization.sas.e2e.fixtures;

import com.jeppesen.carmen.customization.sas.e2e.fixtures.entity.Period;
import com.jeppesen.carmen.customization.sas.e2e.infrastructure.CrewPortalProps;
import lombok.RequiredArgsConstructor;
import org.springframework.cglib.core.Local;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.Properties;

@Service
@RequiredArgsConstructor
public class PeriodsDraftFixture {

    final CrewPortalProps props;

    public Period initDraft() {
        String dateFromProps = props.getAdministrationPage().getPeriodStartDate();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
        LocalDateTime today = LocalDateTime.parse(dateFromProps, formatter);

        return new Period().setType("standard")
                .setStartDate(today)
                .setEndDate(today.plusMonths(2))
                .setOpenDate(today)
                .setCloseDate(today.plusMonths(2));
    }
}
