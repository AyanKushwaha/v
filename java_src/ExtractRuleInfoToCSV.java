import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;

import com.carmensystems.parsers.diff.MultiRulesetProperties;
import com.carmensystems.parsers.diff.RulesetCollectionDifference;
import com.carmensystems.parsers.diff.RulesetComparer;
import com.carmensystems.parsers.diff.RulesetDifference;
import com.carmensystems.parsers.diff.MultiRulesetProperties.RaveDefinitionFilter;
import com.carmensystems.parsers.diff.RulesetDifference.DiffNode;
import com.carmensystems.parsers.parser.ProductType;
import com.carmensystems.parsers.parser.RaveException;
import com.carmensystems.parsers.rave.parser.FileResourceStreamProvider;
import com.carmensystems.parsers.rave.parser.NullErrorHandler;
import com.carmensystems.parsers.rave.parser.RaveCodeModel;
import com.carmensystems.parsers.rave.parser.RaveCompilationUnit;
import com.carmensystems.parsers.rave.parser.RaveConstraint;
import com.carmensystems.parsers.rave.parser.RaveDefinition;
import com.carmensystems.parsers.rave.parser.RaveExpression;
import com.carmensystems.parsers.rave.parser.RaveObject;
import com.carmensystems.parsers.rave.parser.RaveRemark;
import com.carmensystems.parsers.rave.parser.RaveRule;
import com.carmensystems.parsers.rave.parser.RaveTable;
import com.carmensystems.parsers.rave.parser.RaveVariable;
import com.carmensystems.parsers.rave.parser.Ruleset;
import com.carmensystems.parsers.rave.parser.RulesetInstance;
import com.carmensystems.parsers.rave.parser.TreeAction;
import com.carmensystems.parsers.rave.parser.RaveCodeModel.LookupType;
import com.carmensystems.parsers.rave.parser.RaveCodeModel.RaveParserSourceInput;


public class ExtractRuleInfoToCSV {
	static String CARMUSR;
	static String CARMSYS;
	static MultiRulesetProperties diff;
	static RaveCodeModel parser;

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		try {
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
			System.err.println("Parsing all rulesets in $CARMUSR...");
			FileResourceStreamProvider prov = new FileResourceStreamProvider(src, CARMSYS+"carmusr_default\\crc");
			parser = new RaveCodeModel(new NullErrorHandler(), prov, null);
			diff = new MultiRulesetProperties(parser);
			preload(prov, parser);
			System.err.println("Writing CSV file...");
			System.out.println("Rule,Module,Remark,Rulesets,Planner remark");
			RaveCompilationUnit[] modules = parser.getCompilationUnits();
			Arrays.sort(modules, new Comparator<RaveCompilationUnit>() {
				public int compare(RaveCompilationUnit arg0,
						RaveCompilationUnit arg1) {
					return arg0.getName().compareToIgnoreCase(arg1.getName());
				}
			});
			for(RaveCompilationUnit mod : modules) {
				String rulesets = getRulesets(mod).trim();
				for(RaveDefinition def : mod.getDefinitions()) {
					if(def.isRedefinition()) continue;
					if(def instanceof RaveRule) {
						System.out.print("\"");
						System.out.print(def.getName());
						System.out.print("\",\"");
						System.out.print(mod.getName());
						System.out.print("\",");
						System.out.print(def.getRemarkString().replace(',', ' ').replace('\"', ' ').replace('\n', ' ').replace("\\", "").trim());
						System.out.print(",\"");
						System.out.print(rulesets.replace("\\", "").replace(',', ';').trim());
						System.out.print("\",\"");
						String rmk = def.getRemarkString("planner");
						if(rmk != null) System.out.print(rmk.replace(',', ' ').replace('\"', ' ').replace('\n', ' ').replace("\\", "").trim());
						System.out.println("\"");
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(1);
		}
	}
	
	private static String getRulesets(RaveCompilationUnit mod) {
		return diff.exists(mod).toStringMatching(true, ", ").replace("_", "\\_");
	}
	
	private static void preload(FileResourceStreamProvider prov, RaveCodeModel parser) {
		for(LookupType lt : LookupType.values()) {
			if(lt == LookupType.Etable) continue;
			for(RaveParserSourceInput file : prov.getAllInputs(parser, lt, false)) {
				parser.addCompilationUnit(lt, file);
			}
		}
		parser.loadAll();
	}
}
