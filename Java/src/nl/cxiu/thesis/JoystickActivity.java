package nl.cxiu.thesis;

import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnKeyListener;
import android.widget.EditText;
import android.widget.ToggleButton;

public class JoystickActivity extends Activity {
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        final EditText input_ip = (EditText) findViewById(R.id.input_ip);
        input_ip.setOnKeyListener(new OnKeyListener(){
            public boolean onKey(View v, int keyCode, KeyEvent event) {
                // If the event is a key-down event on the "enter" button
                if ((event.getAction() == KeyEvent.ACTION_DOWN) &&
                    (keyCode == KeyEvent.KEYCODE_ENTER)) {
                  // Perform action on key press
                  return true;
                }
                return false;
            }
        });
        
        final EditText input_port = (EditText) findViewById(R.id.input_port);
        input_port.setOnKeyListener(new OnKeyListener(){
            public boolean onKey(View v, int keyCode, KeyEvent event) {
                // If the event is a key-down event on the "enter" button
                if ((event.getAction() == KeyEvent.ACTION_DOWN) &&
                    (keyCode == KeyEvent.KEYCODE_ENTER)) {
                  // Perform action on key press
                  return true;
                }
                return false;
            }
        });
        
        final ToggleButton tbSendData = (ToggleButton) findViewById(R.id.toggle_send_data);
        tbSendData.setOnClickListener(new OnClickListener() {
        	public void onClick(View v) {
        		if (tbSendData.isChecked()) {
        			// start sending data
        		}
        		else {
                    // stop sending data
        		}
        	}
        });
    }
}