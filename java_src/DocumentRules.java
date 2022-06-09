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


public class DocumentRules {
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
			System.err.println("Writing LaTeX file...");
			System.out.println("\\documentclass[a4paper]{article}");
			System.out.println("\\usepackage[latin1]{inputenc}");
                        // Adding packages for maximal column width
                        //   array:    for defining a new column type
                        System.out.println("\\usepackage{array}");
			System.out.println("\\usepackage{longtable}");
			System.out.println("\\begin{document}");
			System.out.println("\\tableofcontents");
			RaveCompilationUnit[] modules = parser.getCompilationUnits();
			for(RaveCompilationUnit mod : modules) {
				boolean hasHeader = false;
				for(RaveDefinition def : mod.getDefinitions()) {
					if(def.isRedefinition()) continue;
					if(def instanceof RaveRule) {
						if(!hasHeader) {
							hasHeader = moduleHeader(mod);
							System.err.println("Module " + mod.getName());
						}
						//defHeader(def);
						//printRemarks(def);
						//printParameterDifferences(mod, def);
						System.out.println();
					}
				}
			}
			System.out.println();
			Arrays.sort(modules, new Comparator<RaveCompilationUnit>() {
				public int compare(RaveCompilationUnit arg0,
						RaveCompilationUnit arg1) {
					return arg0.getName().compareToIgnoreCase(arg1.getName());
				}
			});
			System.out.println("\\newpage");
			isFirst = true;
			System.out.println("\\section{Rules}");
			for(RaveCompilationUnit mod : modules) {
				boolean hasHeader = false;
				for(RaveDefinition def : mod.getDefinitions()) {
					if(def.isRedefinition()) continue;
					if(def instanceof RaveRule) {
						if(!hasHeader) {
							hasHeader = moduleHeader(mod);
							System.err.println("Module " + mod.getName());
						}
						defHeader(def);
						printRemarks(def);
						printParameterDifferences(mod, def);
						System.out.println();
					}
				}
			}
			System.out.println();
			System.out.println("\\newpage");
			isFirst = true;
			System.out.println("\\section{Constraints}");
			for(RaveCompilationUnit mod : modules) {
				boolean hasHeader = false;
				for(RaveDefinition def : mod.getDefinitions()) {
					if(def instanceof RaveConstraint) {
						if(!hasHeader) hasHeader = moduleHeader(mod);
						defHeader(def);
						printRemarks(def);
						printParameterDifferences(mod, def);
						System.out.println();
					}
				}
			}
			System.out.println("\\end{document}");
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(1);
		}
	}
	
	static void printRemarks(RaveDefinition def) {
		
		String rem = def.getRemarkString();
		if(rem != null && rem.length() > 0) {
			System.out.println(rem.replace("\"", "").replace("_", "\\_"));
		} else {
			System.out.println("No remarks");
		}
		rem = def.getRemarkString("planner");
		if(rem != null && rem.length() > 0) {
			rem = rem.trim().replace("\"", "").replace("_", "\\_");
			if(rem.length() > 0) {
				System.out.println("\\\\");
				System.out.println("{\\bf Planner remark:} " + rem);
			}
		}
	}
	
	static String getRulesets(RaveCompilationUnit mod) {
		return diff.exists(mod).toStringMatching(true, ", ").replace("_", "\\_");
	}
	
	/*static String getRulesets(RaveDefinition def) {
		RaveExpression ref = parser.parseExpressionWithoutBinding(def.getDefinedQualifiedName());
		return diff.exists(ref).toStringMatching(true, ", ");
	}*/
	
	static class ParameterFilter implements RaveDefinitionFilter {
		public boolean filter(RaveDefinition d) {
			return d.isParameter();
		}
	}
	
	static class EtableFilter implements RaveDefinitionFilter {
		public boolean filter(RaveDefinition d) {
			if(d instanceof RaveVariable) {
				RaveTable t = ((RaveVariable)d).getDefiningTable();
				if(t != null) return t.isExternal();
			}
			return false;
		}
	}
	
	static void printParameterDifferences(RaveCompilationUnit mod, RaveDefinition def) {
		RaveExpression ref;
		try {
			ref = parser.parseExpressionWithoutBinding(def.getDefinedQualifiedName());
			System.out.println("\\\\");
			// Parameters
			String rulesets = getRulesets(mod).trim();
			RulesetCollectionDifference<RaveDefinition> diffdef = diff.getDependencies(ref, true, new ParameterFilter());
			ArrayList<RaveDefinition> k = diffdef.keys();
			boolean didPrintHeader = false;
			if(k.size() > 0) {
				if(!didPrintHeader) {
					System.out.println("{\\bf Depends on}");
					didPrintHeader = true;
					System.out.println("\\\\");
					System.out.println("\\begin{longtable}{|p{5cm}|p{5cm}|p{4cm}|}");
				}
				System.out.println("\\hline");
				System.out.println("Parameter & Module & Default value \\\\");
				System.out.println("\\hline");
				System.out.println("\\endfirsthead");
				for(RaveDefinition d : k)  {
					String val = "";
					if(d instanceof RaveVariable) {
						val = ((RaveVariable)d).getValue();
					}
					System.out.println(ttlatex(d.getName(), 20) + " & " + ttlatex(d.getCompilationUnit().getName()) + " & " + ttlatex(val) + " \\\\");
				}
	
				//def.getDependencies(ctx, getRefsToDeps, type, oc)
				System.out.println("\\hline");
			}

			// External tables
			RulesetCollectionDifference<String> diffdef2 = getEtableDeps(ref);
			ArrayList<String> k2 = diffdef2.keys();
			if(k2.size() > 0) {
				if(!didPrintHeader) {
					System.out.println("{\\bf Depends on}");
					System.out.println("\\\\");
					System.out.println("\\begin{longtable}{|p{5cm}|p{5cm}|p{4cm}|}");
				}
				System.out.println("\\hline");
				System.out.println("Etable & Ruleset &  \\\\");
				System.out.println("\\hline");
				if(!didPrintHeader) {
				    didPrintHeader = true;
				    System.out.println("\\endfirsthead");
				}
				for(String s : k2)  {
					DiffNode[] dn = diffdef2.get(s);
					String match = "";
					if(dn.length == 0) match = "*";
					else if(dn.length == 1) match = dn[0].toString();
					else {
						StringBuilder sb = new StringBuilder(dn[0].toString());
						for(int i=1;i<dn.length;i++) {
							sb.append(", ");
							sb.append(dn[i].toString());
						}
						match = sb.toString();
					}
					match = match.trim();
					if(match.equalsIgnoreCase(rulesets)) {
						match = "(all)";
					} else {
						match = ttlatex(match);
					}
					System.out.println(ttlatex(s, 20) + " & " + match + " & \\\\");
				}
				System.out.println("\\hline");
			}
			if(didPrintHeader) {
				System.out.println("\\end{longtable}");
			}
		} catch (RaveException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	static RulesetCollectionDifference<String> getEtableDeps(final RaveExpression ref) {
		try {
			return new RulesetCollectionDifference<String>(new RulesetComparer<Iterable<String>>() {
				public Iterable<String> getComparableProperty(
						final RulesetInstance ri) throws RaveException {
					final ArrayList<String> tabs = new ArrayList<String>();
					final ArrayList<RaveObject> taken = new ArrayList<RaveObject>();
					if(ref.bind(ri)) {
						RaveObject def = ref.getReferencedDefinition(ri);
						((RaveDefinition)def).traverseDependencies(ri, 0, new TreeAction() {
							@Override
							public void invoke(int level, RaveObject parent, RaveObject self) {
								if(self instanceof RaveVariable) {
									if(taken.contains(self)) return;
									taken.add(self);
									RaveTable t = ((RaveVariable)self).getDefiningTable();
									if(t != null && t.isExternal()) {
										String n = t.getExternalTableName(ri);
										if(n == null) n = "=" + t.getExternalTableReference().describe();
										if(!tabs.contains(n)) tabs.add(n);
									}
								}
							}
						});
					}
					return tabs;
				}
			}, parser, true);
		} catch (RaveException ex) {
			// never thrown
			throw new RuntimeException();
		}
	}

	static String ttlatex(String n, int nsplit) {
		return "{\\tt " + latex(n, nsplit, "}... & & \\\\\n  {\\tt ") + "}";
	}

	static String ttlatex(String n) {
		return ttlatex(n, 1000);
	}

	static String latex(String n, int nsplit) {
		return latex(n, nsplit, "... \\\\\n  ");
	}
	static String latex(String n, int nsplit, String sep) {
		if(n.length() > nsplit+4) {
			int splitAt = nsplit;
			for(int i=nsplit; i> nsplit-5 && i > 0; i--) {
				char c = n.charAt(i);
				if(c == '_' || c == '-' || c == ' ') {
					splitAt = i;
					break;
				}
			}
			return n.substring(0, splitAt).replace("_", "\\_").replace("%", "\\%") + sep + latex(n.substring(splitAt),nsplit, sep);
		}
		return n.replace("_", "\\_").replace("%", "\\%");
	}
	static String latex(String n) {
		return latex(n, 1000);
	}
	static boolean isFirst = false;
	static boolean moduleHeader(RaveCompilationUnit mod) {
		System.out.println();
		if(!isFirst) System.out.println("\\newpage");
		isFirst = false;
		System.out.println("\\subsection{Module {\\tt " + latex(mod.getName()) + "}}");
		if(mod.isRuleset()) {
			System.out.println("This is the root of a ruleset.");
		} else {
			String s = getRulesets(mod).trim();
			if(s.length() > 0) System.out.println("Exists in rulesets {\\bf " + s + "}");
		}
		return true;
	}
	static boolean defHeader(RaveDefinition def) {
		System.out.println();
		System.out.println("\\subsubsection{\\tt{" + latex(def.getName()) + "}}");
		return true;
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
