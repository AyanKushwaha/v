package com.jeppesen.jcms.customization.template.parsing;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.when;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import com.jeppesen.jcms.customization.sas.parsing.SASRoleMapper;

@RunWith(MockitoJUnitRunner.class)
public class SASRoleMapperTest {

	@Mock
	private UserData user;

	private SASRoleMapper testee = new SASRoleMapper();;

	@Test
	public void sasExportsOnlyOneSingleCacsRole_mapperReturnCrew() {

		// Hardcoded old roles for a crew
		ArrayList<String> crewOldInputRoles = new ArrayList<>();
		crewOldInputRoles.add("interbids-bidding-crew");
		crewOldInputRoles.add("vacation-bidding");
		crewOldInputRoles.add("career-bidding");
		
		when(user.getRoles()).thenReturn(crewOldInputRoles);
		Iterable<String> cacseRoles = testee.getCacsRolesForUser(user);
		assertEquals("crew", cacseRoles.iterator().next());
	}


	@Test
	public void sasExportsOnlyOneSingleCacsRole_mapperReturnAdministrator() {
		when(user.getRoles()).thenReturn(aList("NotAValidRole"));
		Iterable<String> cacseRoles = testee.getCacsRolesForUser(user);
		assertEquals("crew", cacseRoles.iterator().next());
	}
	
	@Test
	public void exportAdminUser() {
		when(user.getRoles()).thenReturn(aList("porta-administrator"));
		Iterable<String> cacseRoles = testee.getCacsRolesForUser(user);
		assertEquals("administrator", cacseRoles.iterator().next());
	}

	
	private List<String> aList(String... args) {
		return Arrays.asList(args);
	}

}
