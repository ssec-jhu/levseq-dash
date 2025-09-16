var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.shortenMutagenesisMethod = function(params) {

  if (params === 'Site Specific') {
    return 'Site';
  } else if (params === 'Across Sequence') {
    return 'Sequence';
  } else
    return params;
};