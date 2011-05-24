import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Properties;

public class Toolkit {
  public static Properties getSettings(String... settingsPaths) {
    Properties p = new Properties();
    if (settingsPaths.length == 0) {
      settingsPaths = new String[] {"../settings.ini"};
    }

    try {
      for (String path : settingsPaths) {
        p.load(new FileInputStream(path));
      }
    }
    catch (Exception e) {
      System.out.println("Probably couldn't find the file.");
    }

    return p;
  }

  public static void main(String... args){
    Properties p = getSettings();
    p.list(System.out);
  }
}
