import java.io.File;

import com.carmensystems.parsers.parser.ProductType;
import com.carmensystems.parsers.rave.parser.FileResourceStreamProvider;
import com.carmensystems.parsers.rave.parser.NullErrorHandler;
import com.carmensystems.parsers.rave.parser.RaveCodeModel;
import com.carmensystems.parsers.rave.parser.RaveDefinition;
import com.carmensystems.parsers.rave.parser.RaveExpression;
import com.carmensystems.parsers.rave.parser.RaveRule;
import com.carmensystems.parsers.rave.parser.Ruleset;
import com.carmensystems.parsers.rave.parser.RulesetInstance;
import com.carmensystems.parsers.rave.parser.RaveCodeModel.LookupType;
import com.carmensystems.parsers.rave.parser.RaveCodeModel.RaveParserSourceInput;


public class FindRulesWithoutBinop {
	static String CARMUSR = "\\\\wake\\rickard\\work\\Customization\\sk_cms_user\\";
	static String CARMSYS = "\\\\wake\\rickard\\work\\Customization\\sk_cms_user\\current_carmsys_cct\\";

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if(args.length != 1) {
			System.err.println("Expected $CARMUSR as first and only arg");
			return;
		}
		CARMUSR = args[0];
		if(CARMUSR.charAt(CARMUSR.length()-1) != '/') {
			CARMUSR += "/";
		}
		CARMSYS = CARMUSR + "current_carmsys_cct";
		String src = CARMUSR+"crc/";
		if(!new File(src).isDirectory()) {
			System.err.println("Directory '" + src + "' does not exist.");
			return;
		}
		FileResourceStreamProvider prov = new FileResourceStreamProvider(CARMUSR+"crc\\", CARMSYS+"carmusr_default\\crc");
		RaveCodeModel parser = new RaveCodeModel(new NullErrorHandler(), prov, null);
		preload(prov, parser);
		for(Ruleset rst : parser.getRulesets()) {
			System.out.println("Ruleset: " + rst.getName());
			int ct = 0;
			RulesetInstance rsi = rst.getInstance(ProductType.STUDIO);
			for(RaveDefinition def : rsi.getDefinitions(false)) {
				if(def instanceof RaveRule) {
					RaveExpression d = ((RaveRule)def).getCondition();
					if(d == null) {
					} else if(d.getOperandCount() != 2) { 
						System.out.println("   " + def.getQualifiedName(rsi));
						System.out.println("       " + d);
						ct++;
					}
				}
			}
			System.out.println("" + ct + " potential problems in " + rst.getName());
		}

	}

	static void preload(FileResourceStreamProvider prov, RaveCodeModel parser) {
		for(LookupType lt : LookupType.values()) {
			if(lt == LookupType.Etable) continue;
			for(RaveParserSourceInput file : prov.getAllInputs(parser, lt, false)) {
				parser.addCompilationUnit(lt, file);
			}
		}
		parser.loadAll();
	}
}
