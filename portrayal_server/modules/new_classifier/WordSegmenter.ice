#ifndef __WORDSEG_ICE__
#define __WORDSEG_ICE__

module bfd {
  sequence<string> StringSeq;
  interface WordSegmenter {
    ["ami", "amd"] int Segment(string text, out StringSeq words);
  };
};

#endif
