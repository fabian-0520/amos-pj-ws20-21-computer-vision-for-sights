using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class moveCamera : MonoBehaviour
{
    List<Vector3> positions = new List<Vector3>();
    int i = 0;

    public Transform target;
    private GameObject sight;
    private script_Sight _sightScript;

    // Start is called before the first frame update
    void Start()
    {
        positions.Add(new Vector3(-28.27f, 0.5f, -38.25f));
        positions.Add(new Vector3(38.5f, 0.5f, 16.13f));

        _sightScript = sight.GetComponent<script_Sight>();
    }

    // Update is called once per frame
    void Update()
    {        
        if (Input.GetKeyDown(KeyCode.Space))
        {
            transform.position = positions[i];
            Vector3 relativePos = script_Sight.position - transform.position;
            transform.rotation = Quaternion.LookRotation(relativePos,new Vector3(0,1,0));


            i++;
            if (i == positions.Count)
            {
                i = 0;
            }
        }
           
    }
}
