%%
%% This is file `nobs.cls',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% nobs.dtx  (with options: `nobs')
%% 
%% IMPORTANT NOTICE:
%% 
%% For the copyright see the source file.
%% 
%% Any modified versions of this file must be renamed
%% with new filenames distinct from nobs.cls.
%% 
%% For distribution of the original source see the terms
%% for copying and modification in the file nobs.dtx.
%% 
%% This generated file may be distributed as long as the
%% original source files, as listed above, are part of the
%% same distribution. (The sources need not necessarily be
%% in the same archive or directory.)
%% \CharacterTable
%%  {Upper-case    \A\B\C\D\E\F\G\H\I\J\K\L\M\N\O\P\Q\R\S\T\U\V\W\X\Y\Z
%%   Lower-case    \a\b\c\d\e\f\g\h\i\j\k\l\m\n\o\p\q\r\s\t\u\v\w\x\y\z
%%   Digits        \0\1\2\3\4\5\6\7\8\9
%%   Exclamation   \!     Double quote  \"     Hash (number) \#
%%   Dollar        \$     Percent       \%     Ampersand     \&
%%   Acute accent  \'     Left paren    \(     Right paren   \)
%%   Asterisk      \*     Plus          \+     Comma         \,
%%   Minus         \-     Point         \.     Solidus       \/
%%   Colon         \:     Semicolon     \;     Less than     \<
%%   Equals        \=     Greater than  \>     Question mark \?
%%   Commercial at \@     Left bracket  \[     Backslash     \\
%%   Right bracket \]     Circumflex    \^     Underscore    \_
%%   Grave accent  \`     Left brace    \{     Vertical bar  \|
%%   Right brace   \}     Tilde         \~}
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newlength{\tmp@len}
\RequirePackage{ifthen}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\PassOptionsToClass{a4paper}{article}
\DeclareOption{a4paper}{}
\DeclareOption {a5paper}{%
  \errhelp{nobs is designed for A4 paper.}
  \errmessage{Unsupported paper size a5paper,
    please use a4paper}}
\DeclareOption {b5paper}{%
  \errhelp{nobs is designed for A4 paper.}
  \errmessage{Unsupported paper size b5paper,
    please use a4paper}}
\DeclareOption {letterpaper}{%
  \errhelp{nobs is designed for A4 paper.}
  \errmessage{Unsupported paper size letterpaper,
    please use a4paper}}
\DeclareOption {legalpaper}{%
  \errhelp{nobs is designed for A4 paper.}
  \errmessage{Unsupported paper size legalpaper,
    please use a4paper}}
\DeclareOption {executivepaper}{%
  \errhelp{nobs is designed for A4 paper.}
  \errmessage{Unsupported paper size executivepaper,
    please use a4paper}}
\newcommand{\OptPtsize}{11pt}
\DeclareOption {10pt} {\renewcommand{\OptPtsize}{10pt}}
\DeclareOption {11pt} {\renewcommand{\OptPtsize}{11pt}}
\DeclareOption {12pt} {\renewcommand{\OptPtsize}{12pt}}
\newcommand{\OptXside}{oneside}
\DeclareOption {oneside} {\renewcommand{\OptXside}{oneside}}
\DeclareOption {twoside} {\renewcommand{\OptXside}{twoside}}
\DeclareOption {landscape} {%
  \errhelp{nobs is designed for portrait printing only.}
  \errmessage{nobs is designed for portrait printing only.}}
\DeclareOption {draft} {\PassOptionsToClass{draft}{article}}
\DeclareOption {final} {\PassOptionsToClass{final}{article}}
\DeclareOption {titlepage} {%
  \errhelp{nobs does not support the titlepage option.}
  \errmessage{nobs does not support the titlepage option.}}
\DeclareOption {notitlepage} {%
  \errhelp{nobs does not support the notitlepage option.}
  \errmessage{nobs does not support the notitlepage option.}}
\PassOptionsToClass{onecolumn}{article}
\DeclareOption {onecolumn} {\PassOptionsToClass{onecolumn}{article}}
\DeclareOption {twocolumn} {\PassOptionsToClass{twocolumn}{article}}
\DeclareOption {leqno}
  {\PassOptionsToClass{leqno}{article}}
\DeclareOption {fleqn}
  {\PassOptionsToClass{fleqn}{article}}
\DeclareOption {openbib}
  {\PassOptionsToClass{openbib}{article}}
\newif\if@langswedish\@langswedishfalse
\DeclareOption {svenska} {\@langswedishtrue}
\newif\if@largepages\@largepagesfalse
\DeclareOption {largepages} {%
  \@largepagestrue%
}
\DeclareOption {bookstyle} {%
  \AtEndOfClass{\pagestyle{bookstyle}}
}
\newif\if@techdoc\@techdocfalse
\DeclareOption {techdoc} {%
  \@techdoctrue%
  \AtEndOfClass{\pagestyle{techdoc}}
}
\newif\if@etechdoc\@etechdocfalse
\DeclareOption {etechdoc} {%
  \@etechdoctrue%
  \AtEndOfClass{\pagestyle{etechdoc}
    \renewenvironment{abstract}{\section*{\abstractname}}{}}
}
\newif\if@pdfserif\@pdfseriffalse
\newif\if@pdfsans\@pdfsansfalse
\DeclareOption {pdfserif} {\@pdfseriftrue}
\DeclareOption {pdfsans}  {\@pdfsanstrue}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\ProcessOptions
\LoadClass[\OptXside,\OptPtsize]{article}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\@ifundefined{pdfoutput}
  {\RequirePackage[dvips]{graphicx}%
   \RequirePackage[dvips]{color}}
  {\RequirePackage[pdftex]{graphicx}%
   \RequirePackage[pdftex]{color}%
   \AtBeginDocument{%
     \DeclareGraphicsExtensions{.pdf,.jpg,.mps,.png}}}
\RequirePackage{verbatim}
\RequirePackage{calc}
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\def\@secondoffive#1#2#3#4#5{#2}
\AtBeginDocument{%
  \@ifundefined{r@LastPage}
    {\def\Last@Page{?}}
    {\edef\Last@Page{\expandafter\@secondoffive\r@LastPage}}
}%
\AtEndOfClass{%
\@ifundefined{pdfoutput}
  {\RequirePackage{hyperref}}
  {\RequirePackage[pdftex,
                   colorlinks=true,
                   linkcolor=black,
                   plainpages=false,
                   bookmarksopen=false]{hyperref}}}
%%%\@ifundefined{pdfoutput}
%%%  {}
%%%  {\RequirePackage{thumbpdf}}
\if@langswedish
  \typeout{loading babel, with Swedish as default}
  \RequirePackage[english,swedish]{babel}
  \AtBeginDocument{\def\abstractname{Referat}}
  \AtEndOfClass{\newcommand{\DocAuthorName}{Författare}%
                \newcommand{\DocDocIdName}{Dok.id}%
                \newcommand{\DocDateName}{Datum}%
                \newcommand{\etech@PreparedName}{Uppgjord}%
                \newcommand{\etech@ApprovedName}{Godkänd}%
                \newcommand{\etech@RefName}{Referens}}
\else
  \typeout{loading babel, with English as default}
  \RequirePackage[swedish,english]{babel}
  \AtEndOfClass{\newcommand{\DocAuthorName}{Author}%
                \newcommand{\DocDocIdName}{Doc.id}%
                \newcommand{\DocDateName}{Date}%
                \newcommand{\etech@PreparedName}{Prepared}%
                \newcommand{\etech@ApprovedName}{Approved}%
                \newcommand{\etech@RefName}{Reference}}
\fi
\RequirePackage{tabularx}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\parskip    0.5em
\parindent  0.0ex
\RequirePackage[a4paper,portrait,includeheadfoot]{geometry}
\geometry{hmargin=30mm, vmargin={15mm,15mm}, headheight=30pt}
\if@etechdoc
\geometry{hmargin=40mm, vmargin={15mm,15mm},
  headheight=30mm, headsep=10mm, footskip=15mm}
\else
\if@techdoc
\geometry{hmargin=25mm, vmargin={15mm,15mm},
  headheight=16mm, headsep=15mm, footskip=15mm}
\fi
\fi

\if@twocolumn
\geometry{hmargin=25mm}
\fi

\if@largepages
\geometry{hmargin=20mm, vmargin={15mm,10mm}}
\fi
%%      Define the DocHdrGraphic and DocHdrLogo macros, used to set
%%      graphic printed in header for some page layouts (etechdoc,
%%      techdoc).  Note that DocHdrGraphic should contain a full
%%      includegraphics specification (it is called for etechdoc page
%%      style), while DocHdrLogo simply points to a file (it is used
%%      within an includegraphics for techdoc page styles).
\newcommand{\DocHdrGraphic}[1]{%
  \renewcommand{\theDocHdrGraphic}{#1}}
\newcommand{\theDocHdrGraphic}{}
\newcommand{\DocHdrLogo}[1]{%
  \renewcommand{\theDocHdrLogo}{#1}}
\newcommand{\theDocHdrLogo}{}
%% Lengths for header logo (max) height and width (logo is scaled to
%% this size).
\newlength{\Doc@HdrLogoHeight}\setlength{\Doc@HdrLogoHeight}{14mm}
\newlength{\Doc@HdrLogoWidth}\setlength{\Doc@HdrLogoWidth}{34mm}
\renewcommand{\headrulewidth}{0pt} %% {0.4pt}
\renewcommand{\footrulewidth}{0pt} %% {0.4pt}
\fancyhf{} % clear all header and footer fields
\fancyhead[C]{{\raisebox{\baselineskip}{\sffamily\bfseries\theDocSecClass}}}
\fancyfoot[C]{\thepage{} (\Last@Page)}
\fancypagestyle{bookstyle}{%
  \renewcommand{\headrulewidth}{0.4pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyhf{} % clear all header and footer fields
  \fancyhead[C]{{\raisebox{\baselineskip}{\sffamily\bfseries\theDocSecClass}}}
  \fancyhead[LO]{\sffamily\rightmark}
  \fancyhead[RE]{\sffamily\leftmark}
  \fancyhead[RO,LE]{\small\sffamily\thepage{} (\Last@Page)}
}
\newlength{\dtw}
\setlength{\dtw}{\textwidth}
%% Hdr text including version, NOT using this for now.
%% \newcommand{\td@hdrA}{%
%%   \raisebox{2pt}{\parbox[b]{\dtw-\Doc@HdrLogoWidth}{%
%%     \@title\medskip\\ Version \theDocRevision\enskip\@date}}}
\newcommand{\td@hdrA}{%
  \raisebox{2pt}{\parbox[b]{\dtw-\Doc@HdrLogoWidth-2em}{%
    \@title}}}
\newcommand{\td@hdrB}{%
  \ifthenelse{\equal{\theDocHdrLogo}{}}{}{%
      \includegraphics[height=\Doc@HdrLogoHeight,%
        width=\Doc@HdrLogoWidth,keepaspectratio]%
        {\theDocHdrLogo}}}
\fancypagestyle{techdoc}{%
  \renewcommand{\headrulewidth}{0.4pt}
  \renewcommand{\footrulewidth}{0.0pt}
  \fancyhf{} % clear all header and footer fields
  \fancyhead[LO]{\td@hdrA}
  \fancyhead[RO]{\td@hdrB}
  \fancyfoot[RO]{\small\thepage{} (\Last@Page)}
  \fancyfoot[LO]{\small\theDocSecClass}
  \fancyfoot[C]{\small\theDocCopyright}
  %%% \fancyfoot[LO]{\footnotesize\theDocIdentity{}\enskip\theDocRevision{}%
}
\newlength{\tw}
\setlength{\tw}{\textwidth +40truemm}
\newcommand{\xxhtz}{\small}
\newcommand{\etechdoc@hdr}{%
  \begin{sffamily}%
    \begin{tiny}%
      \begin{tabular}[t]{@{}|p{.47\tw}@{}|p{.17\tw}@{}p{.08\tw}@{}|p{.25\tw}@{}}
         \multicolumn{1}{l}{ } &
         \multicolumn{3}{l}{\raisebox{0pt}[1.6\height]{\xxhtz{\theDocSecClass}}} \\
         \multicolumn{1}{l}{\raisebox{0pt}[1ex]%
           \theDocHdrGraphic{}} &
         \multicolumn{3}{l}{\raisebox{0pt}[1.6\height][\height]{\xxhtz{\theDocType}}
           \hfill\xxhtz{\thepage (\Last@Page)}} \\
         \hline\raisebox{0pt}[1.6\height]\etech@PreparedName{} &
         \DocDocIdName{} \\
         \xxhtz\raisebox{0pt}[1.4\height][.6\height]{\@author} &
         \multicolumn{3}{l}{\xxhtz{\theDocIdentity}} \\ \hline
         \raisebox{0pt}[1.6\height]\etech@ApprovedName{} & \DocDateName{} &
         Rev & \etech@RefName{} \\
         \xxhtz\raisebox{0pt}[1.4\height][.6\height]{\theDocApproved} &
         \xxhtz\raisebox{0pt}[1.4\height][.6\height]{\today} &
         \xxhtz{\theDocRevision} & \xxhtz{\theDocFileRef} \\
         \hline
      \end{tabular}
    \end{tiny}
  \end{sffamily}}
\fancypagestyle{etechdoc}{%
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyhf{} % clear all header and footer fields
  %% header is at offset -20mm (it's 40mm wider than text body)
  \fancyhfoffset{20truemm}
  \fancyfoot[LO]{\tiny \theDocFileRefLong}
  \fancyhead[L]{\etechdoc@hdr}
}
\fancypagestyle{TitlePage}{%
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyhf{} % clear all header and footer fields
  \fancyhead[C]{{\raisebox{\baselineskip}{\sffamily\bfseries\theDocSecClass}}}
  \fancyfoot[C]{\thepage{} (\Last@Page)}
}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\theRevisionCVS}{}
\def\RevisionCVS $#1${%
  \rcsSplitField #1: {} :\endSplit
  \@IfEmpty\rcsValue{\renewcommand{\theRevisionCVS}{}}
                    {\renewcommand{\theRevisionCVS}{\rcsValue}}}
\newcommand{\theRevisionSVN}{}
\def\RevisionSVN $#1${%
  \rcsSplitField #1: {} :\endSplit
  \@IfEmpty\rcsValue{\renewcommand{\theRevisionSVN}{}}
                    {\renewcommand{\theRevisionSVN}{\rcsValue}}}
\def\DateCVS $#1${%
  \rcsSplitField #1: {} :\endSplit
  \@IfEmpty\rcsValue{}
    {\expandafter\rcsSetDate\rcsValue\endSetDate }
  }%
\def\DateSVN $#1${%
  \rcsSplitField #1: {} :\endSplit
  \@IfEmpty\rcsValue{}
    {\expandafter\svnSetDate\rcsValue\endSetDate }
  }%
\def\rcsSplitField #1: #2 :#3\endSplit{%
    \def\rcsKeyword{#1}%
    \def\rcsValue{#2}%
    }
\def\rcsSetDate #1/#2/#3 #4\endSetDate{%
  \day=#3                 % <-- space!
  \month=#2               % <-- space!
  \year=#1                % <-- space!
}
\def\svnSetDate #1-#2-#3 #4\endSetDate{%
  \day=#3                 % <-- space!
  \month=#2               % <-- space!
  \year=#1                % <-- space!
}
\newcommand{\DocApproved}[1]{\renewcommand{\theDocApproved}{#1}}%
\newcommand{\theDocApproved}{}%
\newcommand{\DocIdentity}[1]{\renewcommand{\theDocIdentity}{#1}}%
\newcommand{\theDocIdentity}{}%
\newcommand{\DocRevision}[1]{\renewcommand{\theDocRevision}{#1}}%
\newcommand{\theDocRevision}{}%
\newcommand{\DocFileRef}[1]{\renewcommand{\theDocFileRef}{#1}}%
\newcommand{\theDocFileRef}{}%
\newcommand{\DocFileRefLong}[1]{\renewcommand{\theDocFileRefLong}{#1}}%
\newcommand{\theDocFileRefLong}{}%
\newcommand{\DocSecClass}[1]{\renewcommand{\theDocSecClass}{#1}}%
\newcommand{\theDocSecClass}{}%
\newcommand{\DocType}[1]{\renewcommand{\theDocType}{#1}}%
\newcommand{\theDocType}{Report}%
\newcommand{\DocCompanyName}[1]{\renewcommand{\theDocCompanyName}{#1}}%
\newcommand{\theDocCompanyName}{}%
\newcommand{\DocCopyright}[1]{\renewcommand{\theDocCopyright}{#1}}%
\newcommand{\theDocCopyright}{}%
\newcommand{\DocCompanyAddress}[1]{%
  \renewcommand{\theDocCompanyAddress}{#1}}%
\newcommand{\theDocCompanyAddress}{}%
\newcommand{\DocPdfTitle}[1]{%
  \renewcommand{\theDocPdfTitle}{#1}}
\newcommand{\theDocPdfTitle}{}
\newcommand{\DocPdfAuthor}[1]{%
  \renewcommand{\theDocPdfAuthor}{#1}}
\newcommand{\theDocPdfAuthor}{}
\renewcommand{\maketitle}{%
  \begingroup
  \renewcommand\thefootnote{\@fnsymbol\c@footnote}%
  \def\@makefnmark{\rlap{\@textsuperscript{\normalfont\@thefnmark}}}%
  \long\def\@makefntext##1{\parindent 1em\noindent
          \hb@xt@1.8em{%
              \hss\@textsuperscript{\normalfont\@thefnmark}}##1}%
  \if@twocolumn
    \ifnum \col@number=\@ne
      \Title@Page
    \else
      \twocolumn[\Title@Page]%
    \fi
  \else
    \newpage
    \global\@topnum\z@   % Prevents figures from going at top of page.
    \Title@Page
  \fi
  \if@etechdoc
  \else
    \if@techdoc
    \else
      \thispagestyle{TitlePage}
    \fi
  \fi\@thanks
  \endgroup
  \setcounter{footnote}{0}%
  \global\let\thanks\@gobble
  \global\let\@thanks\@empty
}
\newcommand{\PrintTitle}{%
  %% If PDF output, add bookmark for title
  \@ifundefined{pdfoutput}{}{%
    \pdfbookmark[1]{\@title}{nobspdftitle.\@arabic\c@page}}%
  {\LARGE\bfseries\nohyphens{\@title}\par}}

\newcommand{\Title@Page}{%
\if@etechdoc
  %% etechdoc -- use an "etechdoc" type layout (left aligned, etc)
  \vskip 2em%
  \let \footnote \thanks
  %% Title
  {\PrintTitle}
  \vskip 1.5em%
\else
\if@techdoc
  %% techdoc -- similar to article title page but with version info
  \newpage
  \null
  \vskip 2em%
  \begin{center}%
    \let \footnote \thanks
    %% Title
    {\PrintTitle}
    \vskip 1.5em%
    %% Author
    \begin{tabular}[t]{c}%
      \@author
    \end{tabular}\par
    \vskip 1em%
    %% Version and Date, and DocID (if not empty)
    {Version \theDocRevision\par}
    {\@date\par}%
    \ifthenelse{\equal{\theDocIdentity}{}}{}%
       {\DocDocIdName: \theDocIdentity{}\par}
  \end{center}%
  \par
  \vskip 1.5em%
\else
  %% NOT (e)techdoc -- use normal (article like) title page
  \newpage
  \null
  \vskip 2em%
  \begin{center}%
    \let \footnote \thanks
    %% Title
    {\PrintTitle}
    \vskip 1.5em%
    %% Author
    \begin{tabular}[t]{c}%
      \@author
    \end{tabular}\par
    \vskip 1em%
    %% Date
    {\@date}%
  \end{center}%
  \par
  \vskip 1.5em%
\fi
\fi
}
\newcommand{\DocInfoTechDoc}{%
  \begin{tabular}{@{}ll@{}}
    \emph{\DocAuthorName:} & \begin{tabular}[t]{@{}l}\@author\end{tabular} \\
    \emph{\DocDocIdName:} & \theDocIdentity{}\enskip\theDocRevision{} \\
    \emph{\DocDateName:}  & \@date \\
  \end{tabular}
 % \par
 % \vskip 1.5em%
}
\newcommand{\DocInfoBox}{%
    \begin{tabular}{@{}|l|l|@{}}
      \hline
      Document type  & \theDocType          \\ \hline
      Security class & \theDocSecClass      \\ \hline
      Identity       & \theDocIdentity      \\ \hline
      Approved       & \theDocApproved      \\ \hline
      Date           & \@date             \\ \hline
      Revision       & \theDocRevision      \\ \hline
    \end{tabular}
}
\newcommand{\DocInfoPage}{%
  \begin{minipage}{\textwidth}
    %% If PDF output, add bookmark for info page
    \@ifundefined{pdfoutput}{}{%
      \pdfbookmark[2]{Document information}{nobspdfdocinfo.\@arabic\c@page}
    }%
    \null\vfil
    %% Document title, and author
    \@title\\[2mm]
    \begin{tabular}[t]{@{}c@{}}%
      \@author
    \end{tabular}\par
    \vskip 1em\relax
    %% Copyright
    \theDocCopyright\par
    \vskip 1em\relax
    %% Address and contact info
    \theDocCompanyAddress\par
    \vfil
    %% Version and date
    \vskip 1em\relax
    %% Display the document information box
    \DocInfoBox{}\par
 \end{minipage}
}
\renewcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
                                     {-3.25ex\@plus -1ex \@minus -.2ex}%
                                     {1.5ex \@plus .2ex}%
                                     {\normalfont\normalsize\bfseries}}
\newenvironment{RevisionHistory}%
  {\section*{Revision History}\label{sec:revision-history}%
   \tabularx{\textwidth}{llX}}
  {\endtabularx}
\newcommand{\nobs}{NoBS}
\renewenvironment{quote}
               {\small\list{}{\rightmargin\leftmargin}%
                \item\relax}
               {\endlist}
\renewenvironment{quotation}
{\list{}{\rightmargin\leftmargin}%
 \item\relax}
{\endlist}
\newcommand{\SetVerbatimFont}[1]{%
  \makeatletter
  \def\verbatim@font{\normalfont\ttfamily#1
    \let\do\do@noligs%
    \verbatim@nolig@list}
  \makeatother}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\@IfEmpty}[3]{%
  \ifx #1\relax \else
  \ifx #1\@empty #2\else
    \ifx #1\long@empty #2\else #3\fi
  \fi\fi}
\newcommand\long@empty{}
\newlanguage\langwohyphens
\newcommand\nohyphens[1]{{\language\langwohyphens #1}}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\let\org@tableofcontents=\tableofcontents
\renewcommand\tableofcontents{
  %% If PDF output, add bookmark for contents
  \@ifundefined{pdfoutput}{}{%
    \pdfbookmark[2]{\contentsname}{nobspdfcontent.\@arabic\c@page}
    }%
 \bgroup
 \parskip    \z@
 \org@tableofcontents
 \egroup
}
\renewcommand\l@subsection{\@dottedtocline{2}{1.5em}{2.6em}}
\renewcommand\l@subsubsection{\@dottedtocline{3}{4.1em}{3.6em}}
\renewcommand\l@paragraph{\@dottedtocline{4}{7.7em}{4.6em}}
\renewcommand\l@subparagraph{\@dottedtocline{5}{10.7em}{5.6em}}
\let\org@listoffigures=\listoffigures
\renewcommand\listoffigures{
  %% If PDF output, add bookmark for contents
  \@ifundefined{pdfoutput}{}{%
    \pdfbookmark[2]{\listfigurename}{nobspdfcontent.\@arabic\c@page}
    }%
 \bgroup
 \parskip    \z@
 \org@listoffigures
 \egroup
}
\renewenvironment{thebibliography}[1]
     {\section{\refname}\label{xxx:ref}%
      \@mkboth{\MakeUppercase\refname}{\MakeUppercase\refname}%
      \list{\@biblabel{\@arabic\c@enumiv}}%
           {\settowidth\labelwidth{\@biblabel{#1}}%
            \leftmargin\labelwidth
            \advance\leftmargin\labelsep
            \@openbib@code
            \usecounter{enumiv}%
            \let\p@enumiv\@empty
            \renewcommand\theenumiv{\@arabic\c@enumiv}}%
      \sloppy
      \clubpenalty4000
      \@clubpenalty \clubpenalty
      \widowpenalty4000%
      \sfcode`\.\@m}
     {\def\@noitemerr
       {\@latex@warning{Empty `thebibliography' environment}}%
      \endlist}
\let\ORG@theindex\theindex
\def\theindex{\let\ps@plain\ps@fancy
  %% If PDF output, add bookmark for index
  \@ifundefined{pdfoutput}{}{
    \pdfbookmark[1]{\indexname}{nobspdfindex.\@arabic\c@page}
    }%
  \ORG@theindex}%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\if@etechdoc
\AtBeginDocument{%
  \renewcommand{\today}{%
    \number\year
    -\ifnum\month<10 0\fi\number\month
    -\ifnum\day<10 0\fi\number\day}%
}
\fi
\if@etechdoc
\AtBeginDocument{%
  \renewcommand{\dateswedish}{%
    \renewcommand{\today}{%
      \number\year
      -\ifnum\month<10 0\fi\number\month
      -\ifnum\day<10 0\fi\number\day}%
  }
  \renewcommand{\dateenglish}{%
    \renewcommand{\today}{%
      \number\year
      -\ifnum\month<10 0\fi\number\month
      -\ifnum\day<10 0\fi\number\day}%
  }
}
\fi
\pagestyle{fancy}
\pagenumbering{arabic}
\AtEndOfClass{%
  \RequirePackage[latin1]{inputenc}}
\AtEndOfClass{%
  \RequirePackage[T1]{fontenc}
  \RequirePackage{ae,aecompl}
}
\if@pdfserif
\AtEndOfClass{%
  \typeout{XXX select pdf serif}
  \RequirePackage{times}}
\fi
\if@pdfsans
\AtEndOfClass{%
  \typeout{XXX select pdf sans}
  \RequirePackage{times}%
  \renewcommand{\rmdefault}{phv}}
\fi
\AtBeginDocument{%
  \@ifundefined{pdfoutput}{}{%
    %% Check and set default values (need to be done at begindoc)
    \ifthenelse{\equal{\theDocPdfTitle}{}}%
       {\renewcommand{\theDocPdfTitle}{\@title}}{}
    \ifthenelse{\equal{\theDocPdfAuthor}{}}%
       {\renewcommand{\theDocPdfAuthor}{\@author}}{}
    %% Set PDF info values
    \hypersetup{pdftitle={\theDocPdfTitle}}%
    \hypersetup{pdfauthor={\theDocPdfAuthor}}}}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newcommand{\DocConfig}[1]{%
  \renewcommand{\theDocConfig}{#1}%
  \@input{nobs-\theDocConfig.cfg}}%
\newcommand{\theDocConfig}{}%
%%\AtBeginDocument{%
\AtEndOfClass{%
  \InputIfFileExists{nobs.cfg}{}{}}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\endinput
%%
%% End of file `nobs.cls'.
