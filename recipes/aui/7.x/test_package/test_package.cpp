#include <AUI/Platform/APlatform.h>
#include <AUI/Platform/AWindow.h>
#include <AUI/Platform/Entry.h>
#include <AUI/Util/UIBuildingHelpers.h>
#include <AUI/View/AButton.h>
#include <AUI/View/ALabel.h>
using namespace declarative;
class MainWindow : public AWindow {
 public:
  MainWindow();
};
MainWindow::MainWindow() : AWindow("Project template app", 300_dp, 200_dp) {
  setContents(Centered{Vertical{
      Centered{Label{"Hello world from AUI!"}},
      _new<AButton>("Visit GitHub repo")
          .connect(&AView::clicked, this,
                   [] {
                     APlatform::openUrl("https://github.com/aui-framework/aui");
                   }),
      _new<AButton>("Visit docs")
          .connect(
              &AView::clicked, this,
              [] { APlatform::openUrl("https://aui-framework.github.io/"); }),
      _new<AButton>("Submit an issue")
          .connect(&AView::clicked, this,
                   [] {
                     APlatform::openUrl(
                         "https://github.com/aui-framework/aui/issues/new");
                   }),
  }});
}

int main(int argc, char** argv) {
  _new<MainWindow>()->show();
  return 0;
}
