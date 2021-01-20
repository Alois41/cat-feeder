package com.example.feedercontrol.ui.main

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.example.feedercontrol.MainActivity
import com.example.feedercontrol.R


class Summary : Fragment() {

    private var TextViewWeight: TextView? = null

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_summary, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        TextViewWeight = view.findViewById(R.id.textViewWeight) as TextView?

        val activity: MainActivity = activity as MainActivity
        val button: ImageButton = view.findViewById(R.id.imageButton)
        button.setOnClickListener {
            val t: Thread = Thread { activity.FTPQuery() }
            t.start()
            t.join()
        }

    }

    override fun onStart() {
        super.onStart()
        (activity as MainActivity?)?.summaryStarted()
    }

    fun setWeight(weight: String) {
        Log.d("summary", "set weight")
        TextViewWeight?.text = "Poids: ${weight}g"
    }
}