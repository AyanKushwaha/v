package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc;

import static org.junit.Assert.assertEquals;
import static org.mockito.BDDMockito.given;
import static org.mockito.Matchers.any;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.UUID;

import org.apache.xmlrpc.XmlRpcRequest;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.runners.MockitoJUnitRunner;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps.StringReplacementPostProcessingStep;

@RunWith(MockitoJUnitRunner.class)
public class PostProcessorTest {

	private PostProcessor testee = new PostProcessor();

	private String systemTime = "" + System.currentTimeMillis();
	private String uuid = "" + UUID.randomUUID();
	private String methodName = "feedback_loop_flight";

	@Mock
	private XmlRpcRequest request;

	@Before
	public void setup() {
		testee = new PostProcessor() {
			@Override
			protected String getTimestamp() {
				return systemTime;
			};

			@Override
			protected String getUuid() {
				return uuid;
			};

		};
		when(request.getParameterCount()).thenReturn(1);
		when(request.getParameter(0)).thenReturn("World");
		when(request.getMethodName()).thenReturn(methodName);
	}

	@Test
	public void integerInCurlsIsMagic() throws Exception {
		final String before = "Hello ${0}!";
		final String expected = "Hello World!";

		String after = testee.postProcessResult(before, request);

		assertEquals(expected, after);
	}

	@Test
	public void uuidIsMagic() throws Exception {
		final String before = "xxx${UUID}xxx";
		final String expected = "xxx" + uuid + "xxx";

		String after = testee.postProcessResult(before, request);

		assertEquals(expected, after);
	}

	@Test
	public void timestampIsMagic() throws Exception {
		final String before = "xxx${TIMESTAMP}xxx";
		final String expected = "xxx" + systemTime + "xxx";

		String after = testee.postProcessResult(before, request);

		assertEquals(expected, after);
	}

	@Test
	public void methodIsMagic() throws Exception {
		final String before = "xxx${METHOD}xxx";
		final String expected = "xxx" + methodName + "xxx";

		String after = testee.postProcessResult(before, request);

		verify(request).getMethodName();
		assertEquals(expected, after);
	}

	@Test
	public void typicalUseCase() throws Exception {
		final String before = "from request: ${0} ${METHOD}, from decorator: 1980-${OCTOBER}-15";
		final String expected = "from request: World " + methodName + ", from decorator: 1980-10-15";

		testee.addPostProcessingStep(new StringReplacementPostProcessingStep("OCTOBER", "10"));
		String after = testee.postProcessResult(before, request);

		assertEquals(expected, after);
	}

	@Test
	public void oneCanAddCustomerPostProcessingDecorators() throws Exception {
		final String before = "from request: ${0} ${METHOD}, from decorator: 1980-${OCTOBER}-15";
		PostProcessingStep mock = Mockito.mock(PostProcessingStep.class);
		given(mock.postProcess(anyString(), any(XmlRpcRequest.class))).willReturn("internet");
		testee.addPostProcessingStep(mock);

		String after = testee.postProcessResult(before, request);

		verify(mock).postProcess(anyString(), any(XmlRpcRequest.class));
		assertEquals("internet", after);
	}

}
