package com.sas.authentication;

import com.jeppesen.jcms.crewweb.common.util.CWLog;
import org.jboss.security.SimpleGroup;
import org.jboss.security.SimplePrincipal;
import org.jboss.security.auth.spi.AbstractServerLoginModule;

import javax.security.auth.login.LoginException;
import javax.servlet.http.HttpServletRequest;
import java.security.Principal;
import java.security.acl.Group;

public class SASCookieLoginModule extends AbstractServerLoginModule {

    private final CWLog logger = CWLog.getLogger(SASCookieLoginModule.class);
    private final SASAuthenticationConfiguration configuration;
    private final AuthenticationUtil authenticationUtil;

    private String crewId;

    public SASCookieLoginModule() throws Exception {
        this(new DefaultSASAuthenticationConfiguration());
    }

    public SASCookieLoginModule(SASAuthenticationConfiguration configuration) {
        this(configuration, new AuthenticationUtil());
    }

    public SASCookieLoginModule(SASAuthenticationConfiguration configuration,
                                AuthenticationUtil authenticationUtil) {
        this.configuration = configuration;
        this.authenticationUtil = authenticationUtil;
    }

    @SuppressWarnings("unchecked") // sharedState is a raw Map
    @Override
    public boolean login() throws LoginException {
        HttpServletRequest request = authenticationUtil.getHttpRequest();
        crewId = authenticationUtil.getSessionIdFromMagicCookie(request, configuration.getAuthenticationCookieName());

        if (crewId == null) {
            loginOk = false;
            return false;
        } else {
            subject.getPrincipals().add(new SimplePrincipal(crewId));
            sharedState.put("javax.security.auth.login.name", crewId);
            sharedState.put("javax.security.auth.login.password", configuration.getDummyPassword());
        }

        if (logger.isDebugEnabled()) logger.debug("Performing login using crewId {}", crewId);
        return super.login();
    }

    @Override
    protected Principal getIdentity() {
        return new SimplePrincipal(crewId);
    }

    @Override
    protected Group[] getRoleSets() throws LoginException {
        return new Group[]{new SimpleGroup("Roles")};
    }
}
