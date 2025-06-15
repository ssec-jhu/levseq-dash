var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.shortenMutagenesisMethod = function(params) {

  if (params === 'Site saturation mutagenesis (SSM)') {
    return 'SSM';
  } else if (params === 'Error-prone PCR (epPCR)') {
    return 'epPCR';
  } else
    return params;
};