package com.example.feedercontrol.ui.main

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import androidx.core.widget.doAfterTextChanged
import androidx.fragment.app.Fragment
import com.example.feedercontrol.MainActivity
import com.example.feedercontrol.R


class Settings : Fragment() {
    private lateinit var lilouQ: EditText
    private lateinit var lilouN: EditText
    private lateinit var ReglisseQ: EditText
    private lateinit var ReglisseN: EditText


    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_settings, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        lilouQ = view.findViewById<EditText>(R.id.qLilou)
        lilouN = view.findViewById<EditText>(R.id.nLilou)
        ReglisseQ = view.findViewById<EditText>(R.id.qReglisse)
        ReglisseN = view.findViewById<EditText>(R.id.nReglisse)

        val activity: MainActivity = activity as MainActivity


        view.findViewById<Button>(R.id.buttonSend).setOnClickListener(View.OnClickListener {
            activity.publish(
                "feeder/settings/reglisse/number",
                ReglisseN.text.toString(), retained = true
            )
            activity.publish(
                "feeder/settings/reglisse/quantity",
                ReglisseQ.text.toString(), retained = true
            )
            activity.publish(
                "feeder/settings/lilou/number",
                lilouN.text.toString(), retained = true
            )
            activity.publish(
                "feeder/settings/lilou/quantity",
                lilouQ.text.toString(), retained = true
            )
        })


    }

}