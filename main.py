import sys
from xcllmtool import XCLLMTool
  
if __name__ == "__main__":
    tool = XCLLMTool()
    tool.run(sys.argv[1:])