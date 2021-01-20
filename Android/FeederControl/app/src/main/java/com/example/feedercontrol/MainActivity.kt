package com.example.feedercontrol

import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.media.MediaScannerConnection
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Environment.getExternalStorageDirectory
import android.provider.MediaStore
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager.widget.ViewPager
import com.example.feedercontrol.ui.main.SectionsPagerAdapter
import com.example.feedercontrol.ui.main.Settings
import com.example.feedercontrol.ui.main.Summary
import com.google.android.material.tabs.TabLayout
import org.apache.commons.net.ftp.FTP
import org.apache.commons.net.ftp.FTPClient
import org.apache.commons.net.ftp.FTPFile
import org.eclipse.paho.android.service.MqttAndroidClient
import org.eclipse.paho.client.mqttv3.*
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.File.separator
import java.io.FileOutputStream
import java.io.OutputStream
import java.net.URI


class MainActivity : AppCompatActivity() {

    private lateinit var mqttClient: MqttAndroidClient
    private lateinit var sectionsPagerAdapter: SectionsPagerAdapter

    fun getClient(): MqttAndroidClient {
        return mqttClient
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        sectionsPagerAdapter = SectionsPagerAdapter(this, supportFragmentManager)
        val viewPager: ViewPager = findViewById(R.id.view_pager)
        viewPager.adapter = sectionsPagerAdapter
        val tabs: TabLayout = findViewById(R.id.tabs)
        tabs.setupWithViewPager(viewPager)
    }

    fun FTPQuery() {
        var saved_uri: Uri? = Uri.EMPTY

        try {
            val mFtpClient = FTPClient()
            mFtpClient.connect("feeder", 21)
            mFtpClient.login("pi", "raspberry")
            mFtpClient.enterLocalPassiveMode();
            mFtpClient.changeWorkingDirectory("/files")
            mFtpClient.setFileType(FTP.BINARY_FILE_TYPE)
            mFtpClient.setFileTransferMode(FTP.BLOCK_TRANSFER_MODE)

            val file_list = mFtpClient.listFiles()
            for (file: FTPFile in file_list) {
                val outputStream: ByteArrayOutputStream = ByteArrayOutputStream()
                if (mFtpClient.retrieveFile(
                        "/files/${file.name}", outputStream
                    )
                ) Log.d("FTP", "${file.name} downloaded")
                else Log.d("FTP", "${file.name} failed")

                val bitmapdata = (outputStream).toByteArray();
                val bitmap = BitmapFactory.decodeByteArray(bitmapdata, 0, bitmapdata.size)

                saved_uri = saveImage(bitmap, this, "feeder", file.name)
                outputStream.close()
            }


            mFtpClient.logout()
            mFtpClient.disconnect()

        } catch (e: Exception) {
            e.printStackTrace()
        }
        val intent = Intent(Intent.ACTION_VIEW)
        intent.type = "image/*"
        saved_uri.toString().split("/")
        val values = contentValues()
        //intent.data = Uri.parse(saved_uri.toString())


        if (intent.resolveActivity(packageManager) != null) {
            startActivity(intent)
        }
    }


    fun connect(context: Context) {
        val summary: Summary? =
            supportFragmentManager.findFragmentByTag("android:switcher:" + R.id.view_pager + ":0") as Summary?

        val settings: Settings? =
            supportFragmentManager.findFragmentByTag("android:switcher:" + R.id.view_pager + ":1") as Settings?

        val options = MqttConnectOptions()
        val serverURI = "tcp://feeder:1883"
        mqttClient = MqttAndroidClient(context, serverURI, "kotlin_client")
        mqttClient.setCallback(object : MqttCallback {
            override fun messageArrived(topic: String?, message: MqttMessage?) {
                Log.d(TAG, "Receive message: ${message.toString()} from topic: $topic")
                when (topic) {
                    "feeder/weight" -> summary?.view?.findViewById<TextView>(R.id.textViewWeight)?.text =
                        "Poids: ${message.toString()}g"

                    "feeder/settings/lilou/quantity" -> settings?.view?.findViewById<TextView>(R.id.qLilou)?.text =
                        message.toString()
                    "feeder/settings/lilou/number" -> settings?.view?.findViewById<TextView>(R.id.nLilou)?.text =
                        message.toString()
                    "feeder/settings/reglisse/quantity" -> settings?.view?.findViewById<TextView>(R.id.qReglisse)?.text =
                        message.toString()
                    "feeder/settings/reglisse/number" -> settings?.view?.findViewById<TextView>(R.id.nReglisse)?.text =
                        message.toString()

                    "feeder/history/lilou/last" -> summary?.view?.findViewById<TextView>(R.id.textViewLilou)?.text =
                        "Lilou: ${message.toString()}"

                    "feeder/history/reglisse/last" -> summary?.view?.findViewById<TextView>(R.id.textViewReg)?.text =
                        "Reglisse: ${message.toString()}"

                    else -> Log.d(TAG, "topic non geré")

                }
            }

            override fun connectionLost(cause: Throwable?) {
                Log.d(TAG, "Connection lost ${cause.toString()}")
                try {
                    mqttClient.connect(options, null, object : IMqttActionListener {
                        override fun onSuccess(asyncActionToken: IMqttToken?) {
                            Log.d(TAG, "Connection success")
                            subscribe("feeder/#")
                        }

                        override fun onFailure(
                            asyncActionToken: IMqttToken?,
                            exception: Throwable?
                        ) {
                            Log.d(TAG, "Connection failure")
                        }
                    })
                } catch (e: MqttException) {
                    e.printStackTrace()
                }
            }

            override fun deliveryComplete(token: IMqttDeliveryToken?) {

            }
        })

        try {
            mqttClient.connect(options, null, object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    Log.d(TAG, "Connection success")
                    subscribe("feeder/#")
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    Log.d(TAG, "Connection failure")
                }
            })
        } catch (e: MqttException) {
            e.printStackTrace()
        }

    }

    fun subscribe(topic: String, qos: Int = 1) {
        try {
            mqttClient.subscribe(topic, qos, null, object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    Log.d(TAG, "Subscribed to $topic")
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    Log.d(TAG, "Failed to subscribe $topic")
                }
            })
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }

    fun publish(topic: String, msg: String, qos: Int = 1, retained: Boolean = false) {
        try {
            val message = MqttMessage()
            message.payload = msg.toByteArray()
            message.qos = qos
            message.isRetained = retained
            mqttClient.publish(topic, message, null, object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    Log.d(TAG, "$msg published to $topic")
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    Log.d(TAG, "Failed to publish $msg to $topic")
                }
            })
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }

    fun summaryStarted() {
        connect(this)
    }

    private fun saveImage(
        bitmap: Bitmap,
        context: Context,
        folderName: String,
        filename: String
    ): Uri? {
        if (android.os.Build.VERSION.SDK_INT >= 29) {
            val values = contentValues()
            values.put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/$folderName")
            values.put(MediaStore.Images.Media.IS_PENDING, true)
            values.put(MediaStore.Images.Media.DISPLAY_NAME, filename)
            // RELATIVE_PATH and IS_PENDING are introduced in API 29.

            val uri: Uri? =
                context.contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            if (uri != null) {

                saveImageToStream(bitmap, context.contentResolver.openOutputStream(uri))
                values.put(MediaStore.Images.Media.IS_PENDING, false)
                context.contentResolver.update(uri, values, null, null)


            }
            val builder = Uri.Builder()
            val segments = uri?.pathSegments

            for (i in 0..(segments?.size?.minus(1)!!))
                builder.appendPath(segments[i])

            return builder.build()

        } else {
            val directory = File(getExternalStorageDirectory().toString() + separator + folderName)
            // getExternalStorageDirectory is deprecated in API 29

            if (!directory.exists()) {
                directory.mkdirs()
            }
            val file = File(directory, filename)
            saveImageToStream(bitmap, FileOutputStream(file))
            if (file.absolutePath != null) {
                val values = contentValues()
                values.put(MediaStore.Images.Media.DATA, file.absolutePath)
                // .DATA is deprecated in API 29
                context.contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
            }
            return Uri.fromFile(file)
        }

    }

    private fun contentValues(): ContentValues {
        val values = ContentValues()
        values.put(MediaStore.Images.Media.MIME_TYPE, "image/png")
        return values
    }

    private fun saveImageToStream(bitmap: Bitmap, outputStream: OutputStream?) {
        if (outputStream != null) {
            try {
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, outputStream)
                outputStream.close()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }


    companion object {
        const val TAG = "AndroidMqttClient"
    }
}