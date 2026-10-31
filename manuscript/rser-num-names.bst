%% rser-num-names.bst
%% Numbered (citation-order) BibTeX style following the reference examples in
%% the Renewable and Sustainable Energy Reviews guide for authors:
%%   [1] Van der Geer J, Hanraads JAJ, Lupton RA. The art of writing a
%%       scientific article. J Sci Commun 2020;163:51-9.
%%       https://doi.org/10.1016/j.sc.2020.00372.
%%   [5] Cancer Research UK. Cancer statistics reports for the UK,
%%       http://...; 2023 [accessed 13 March 2023].
%% - first 6 authors, then "et al."
%% - journal abbreviation taken from the `shortjournal' field (LTWA/ISO 4),
%%   falling back to `journal'
%% - last page shortened (51--59 -> 51-9)
%% - `type = {dataset}' prefixes the entry with [dataset]
%% - natbib-compatible \bibitem labels so \citet gives "Author [n]"

ENTRY
  { address author booktitle doi edition editor howpublished institution
    journal shortjournal note number organization pages publisher title
    type url urldate volume year }
  {}
  { label }

INTEGERS { nameptr namesleft numnames pg.i pg.len }
STRINGS { s t pg.s pg.first pg.last }

FUNCTION {not} { { #0 } { #1 } if$ }
FUNCTION {and} { 'skip$ { pop$ #0 } if$ }
FUNCTION {or}  { { pop$ #1 } 'skip$ if$ }

FUNCTION {field.or.null} { duplicate$ empty$ { pop$ "" } 'skip$ if$ }

%% ---------- names ----------
FUNCTION {format.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  ""
  { namesleft #0 > nameptr #7 < and }
  { s nameptr "{vv~}{ll}{ jj}{ f{}}" format.name$ 't :=
    t "others" =
      { nameptr #1 > { "," * } 'skip$ if$ " et al." * }
      { nameptr #1 > { ", " * } 'skip$ if$ t * }
    if$
    nameptr #1 + 'nameptr :=
    namesleft #1 - 'namesleft :=
  }
  while$
  numnames #6 > { ", et al." * } 'skip$ if$
}

FUNCTION {format.authors}
{ author empty$ { "" } { author format.names } if$ }

FUNCTION {format.editors}
{ editor empty$
    { "" }
    { editor format.names
      editor num.names$ #1 > { ", editors" } { ", editor" } if$ *
    }
  if$
}

%% ---------- natbib labels ----------
FUNCTION {format.lab.names}
{ 's :=
  s num.names$ 'numnames :=
  s #1 "{vv~}{ll}" format.name$
  numnames #1 >
    { numnames #2 =
        { s #2 "{ff }{vv }{ll}{ jj}" format.name$ "others" =
            { " et~al." * }
            { " and " * s #2 "{vv~}{ll}" format.name$ * }
          if$
        }
        { " et~al." * }
      if$
    }
    'skip$
  if$
}

FUNCTION {calc.label}
{ author empty$ not
    { author format.lab.names }
    { editor empty$ not
        { editor format.lab.names }
        { organization empty$ not
            { organization }
            { institution empty$ not { institution } { cite$ #1 #3 substring$ } if$ }
          if$
        }
      if$
    }
  if$
  "(" * year field.or.null * ")" *
  'label :=
}

FUNCTION {output.bibitem}
{ newline$
  "\bibitem[{" write$ label write$ "}]{" write$ cite$ write$ "}" write$
  newline$
}

%% ---------- pieces ----------
FUNCTION {short.pages}
{ 'pg.s :=
  "" 'pg.first :=
  #1 'pg.i :=
  pg.s text.length$ 'pg.len :=
  { pg.i pg.len > { #0 } { pg.s pg.i #1 substring$ "-" = not } if$ }
  { pg.first pg.s pg.i #1 substring$ * 'pg.first := pg.i #1 + 'pg.i := }
  while$
  { pg.i pg.len > { #0 } { pg.s pg.i #1 substring$ "-" = } if$ }
  { pg.i #1 + 'pg.i := }
  while$
  pg.s pg.i global.max$ substring$ 'pg.last :=
  pg.last empty$
    { pg.first }
    { pg.first text.length$ pg.last text.length$ =
        { #1 'pg.i :=
          { pg.i pg.last text.length$ <
              { pg.first pg.i #1 substring$ pg.last pg.i #1 substring$ = }
              { #0 }
            if$
          }
          { pg.i #1 + 'pg.i := }
          while$
          pg.first "-" * pg.last pg.i global.max$ substring$ *
        }
        { pg.first "-" * pg.last * }
      if$
    }
  if$
}

FUNCTION {dataset.prefix}
{ type empty$ { "" } { type "dataset" = { "[dataset] " } { "" } if$ } if$ }

FUNCTION {author.part}
{ dataset.prefix
  author empty$
    { editor empty$
        { organization empty$ 'skip$ { organization * ". " * } if$ }
        { format.editors * ". " * }
      if$
    }
    { format.authors add.period$ * " " * }
  if$
}

FUNCTION {title.part}
{ title empty$ { "" } { title add.period$ " " * } if$ }

FUNCTION {doi.url.part}
{ doi empty$
    { url empty$ { "" } { " \url{" url * "}" * } if$ }
    { " \url{https://doi.org/" doi * "}." * }
  if$
}

FUNCTION {note.part}
{ note empty$ { "" } { " " note add.period$ * } if$ }

FUNCTION {journal.name}
{ shortjournal empty$ { journal field.or.null } { shortjournal } if$ }

%% ---------- entry types ----------
FUNCTION {article}
{ output.bibitem
  author.part title.part *
  journal.name * " " * year field.or.null *
  volume empty$
    { pages empty$ 'skip$ { ";" * pages short.pages * } if$ }
    { ";" * volume *
      pages empty$ 'skip$ { ":" * pages short.pages * } if$
    }
  if$
  "." *
  note.part *
  doi.url.part *
  write$ newline$
}

FUNCTION {book}
{ output.bibitem
  author.part
  title empty$ 'skip$ { title add.period$ * " " * } if$
  edition empty$ 'skip$ { edition * " ed. " * } if$
  address empty$ 'skip$ { address * ": " * } if$
  publisher field.or.null * "; " * year field.or.null * "." *
  note.part *
  doi.url.part *
  write$ newline$
}

FUNCTION {incollection}
{ output.bibitem
  author.part title.part *
  "In: " *
  editor empty$ 'skip$ { format.editors * ". " * } if$
  booktitle field.or.null *
  address empty$ { ", " * } { ", " * address * ": " * } if$
  publisher field.or.null * "; " * year field.or.null *
  pages empty$ 'skip$ { ", p. " * pages short.pages * } if$
  "." *
  note.part *
  doi.url.part *
  write$ newline$
}

FUNCTION {inproceedings} { incollection }

FUNCTION {techreport}
{ output.bibitem
  author.part title.part *
  number empty$ 'skip$ { number * ". " * } if$
  address empty$ 'skip$ { address * ": " * } if$
  institution field.or.null * "; " * year field.or.null * "." *
  note.part *
  doi.url.part *
  write$ newline$
}

FUNCTION {misc}
{ output.bibitem
  author.part
  title empty$ 'skip$ { title * } if$
  howpublished empty$ 'skip$ { ", " * howpublished * } if$
  url empty$ 'skip$ { ", \url{" * url * "}" * } if$
  "; " * year field.or.null *
  urldate empty$ 'skip$ { " [accessed " * urldate * "]" * } if$
  "." *
  note.part *
  doi empty$ 'skip$ { " \url{https://doi.org/" * doi * "}." * } if$
  write$ newline$
}

FUNCTION {online} { misc }
FUNCTION {manual} { techreport }
FUNCTION {phdthesis} { book }
FUNCTION {mastersthesis} { book }
FUNCTION {unpublished} { misc }
FUNCTION {default.type} { misc }

%% ---------- driver ----------
READ

ITERATE {calc.label}

FUNCTION {longest.label.pass} { }

FUNCTION {begin.bib}
{ preamble$ empty$ 'skip$ { preamble$ write$ newline$ } if$
  "\begin{thebibliography}{99}" write$ newline$
  "\expandafter\ifx\csname url\endcsname\relax" write$ newline$
  "  \def\url#1{\texttt{#1}}\fi" write$ newline$
}

EXECUTE {begin.bib}

ITERATE {call.type$}

FUNCTION {end.bib} { newline$ "\end{thebibliography}" write$ newline$ }

EXECUTE {end.bib}
