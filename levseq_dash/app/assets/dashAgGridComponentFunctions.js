var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions ||
    {});
// /*
//   Function below is used for the alignment "coordinates" column
// */
// dagcomponentfuncs.addLineBreaksOnArrayRow = function(params) {
//   //console.log(params.value);
//   if (Array.isArray(params.value)) {
//     // Create a parent div to hold all sub-array divs
//     let e;
//     e = React.createElement(
//         'div',
//         {style: {fontSize: '12px'}},
//         // Map each sub-array to a div element
//         params.value.map((subArray, index) =>
//             React.createElement('div', {key: index}, `[${subArray.join(', ')}]`,
//             ),
//         ),
//     );
//     //console.log(e)
//     return e;
//   }
// };

// dagcomponentfuncs.addLineBreaksOnNewLines = function(params) {
//   if (typeof params.value === 'string') {
//     let lines = params.value.split(/\n/);
//     // console.log(lines);
//
//     // Find all the "." in the sequence
//     // need to go over every 4 pairs of lines. the 4th line is empty
//     let results = [];
//     for (let i = 0; i < lines.length - 2; i += 4) {
//       let seq1 = lines[i];      // First sequence line
//       let align = lines[i + 1]; // Alignment line (middle)
//       let seq2 = lines[i + 2];  // Second sequence line
//
//       // Iterate through each character in the alignment line
//       for (let j = 0; j < align.length; j++) {
//         if (align[j] === '.') {
//           // Store row number and index for all three rows
//           results.push({row: i, index: j});     // First sequence
//           results.push({row: i + 1, index: j}); // Alignment row
//           results.push({row: i + 2, index: j}); // Second sequence
//         }
//       }
//     }
//
//     return React.createElement(
//         'div',
//         {
//           style: {
//             fontFamily: 'monospace',
//             whiteSpace: 'pre-wrap',
//             fontSize: '11px',
//             lineHeight: '1.3',
//           },
//         },
//         lines.map((line, lineIndex) => [
//           lineIndex > 0 ? React.createElement('br') : null,
//           ...[...line].map((char, charIndex) => {
//             // Check if the current (row, index) exists in results
//             let shouldHighlight = results.some(
//                 (pos) => pos.row === lineIndex && pos.index === charIndex,
//             );
//
//             return shouldHighlight ? React.createElement('span',
//                 {style: {backgroundColor: '#FFCCCB'}}, char) : char;
//           }),
//         ]),
//     );
//   }
//   return params.value;
// };

dagcomponentfuncs.seqAlignmentVis = function(params) {
  if (typeof params.value === 'string') {
    let lines = params.value.split(/\n/);

    // Find all the "." in the sequence
    // need to go over every 4 pairs of lines.
    // the 4th line is empty
    let results = [];
    for (let i = 0; i < lines.length - 2; i += 4) {
      let seq1 = lines[i];      // First sequence line
      let pipes = lines[i + 1]; // Alignment line (middle)
      let hot_cold = lines[i + 2]; // Alignment line (middle)
      let seq2 = lines[i + 3];  // Second sequence line

      // mutations row
      for (let j = 0; j < hot_cold.length; j++) {
        if (pipes[j] === '.') {
          // Store row number and index for all rows
          results.push({row: i, index: j, type: 'M'});     //  target
          results.push({row: i + 1, index: j, type: 'M'}); // pipes
          //results.push({row: i + 2, index: j, type: 'M'}); // // hot and cold row
          results.push({row: i + 3, index: j, type: 'M'}); // query
        }
      }
      // Iterate through each character in the alignment line
      for (let j = 0; j < hot_cold.length; j++) {
        if (hot_cold[j] === 'H') {
          // Store row number and index for all rows
          results.push({row: i, index: j, type: 'H'});     // target
          results.push({row: i + 1, index: j, type: 'H'}); // pipes row
          //results.push({row: i + 2, index: j, type: 'H'}); // hot and cold row
          results.push({row: i + 3, index: j});           // query
        }
        if (hot_cold[j] === 'C') {
          // Store row number and index for all three rows
          results.push({row: i, index: j, type: 'C'});     // target
          results.push({row: i + 1, index: j, type: 'C'}); // pipes
          //results.push({row: i + 2, index: j, type: 'C'}); // hot and cold row
          results.push({row: i + 3, index: j});           //query
        }
        if (hot_cold[j] === 'B') {
          // Store row number and index for all three rows
          results.push({row: i, index: j, type: 'B'});       // target
          results.push({row: i + 1, index: j, type: 'B'}); // pipes
          //results.push({row: i + 2, index: j, type: 'B'}); // hot and cold row
          results.push({row: i + 3, index: j});           //query
        }

      }
    }
    //console.log(results)

    // This code removes the H C B line
    // comment below  to see H C B for debugging
    // and uncomment the H C B results.push above
    lines.splice(2, 1);

    return React.createElement(
        'div',
        {
          style: {
            fontFamily: 'monospace',
            // keeping here for reference but th style
            // is set in column definitions
            // whiteSpace: 'pre-wrap',
            // fontSize: '10px',
            // lineHeight: '1.1',
          },
        },
        lines.map((line, lineIndex) => [
          lineIndex > 0 ? React.createElement('br') : null,
          ...[...line].map((char, charIndex) => {

            let custom_style;
            let isMutation = results.some(
                (pos) => pos.row === lineIndex && pos.index === charIndex &&
                    pos.type === 'M');
            let isHot = results.some(
                (pos) => pos.row === lineIndex && pos.index === charIndex &&
                    pos.type === 'H');
            let isCold = results.some(
                (pos) => pos.row === lineIndex && pos.index === charIndex &&
                    pos.type === 'C');
            let isColdAndHot = results.some(
                (pos) => pos.row === lineIndex && pos.index === charIndex &&
                    pos.type === 'B');

            if (isCold) {
              custom_style = {
                style: {
                  backgroundColor: '#d0ddfa',
                  color: 'black',
                },
              };
            }
            if (isHot) {
              custom_style = {
                style: {
                  backgroundColor: '#FFCCCB',
                  color: 'black',
                },
              };
            }
            if (isColdAndHot) {
              custom_style = {
                style: {
                  backgroundColor: '#e9d8fd',
                  color: 'black',
                },
              };
            }

            // //uncomment below and comment top for text highlighting
            // if (isCold) {
            //   custom_style = {style: {color: 'blue'}};
            // }
            // if (isHot) {
            //   custom_style = {style: {color: 'red'}};
            // }
            // if (isColdAndHot) {
            //   custom_style = {style: {color: 'purple'}};
            // }

            return isMutation || isHot || isCold || isColdAndHot
                ? React.createElement('span', custom_style, char)
                : char;
          }),
        ]),
    );
  }
  return params.value;
};





