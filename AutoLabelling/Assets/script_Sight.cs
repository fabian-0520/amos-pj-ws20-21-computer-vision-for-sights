using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class script_Sight : MonoBehaviour
{
    public static Vector3 position = new Vector3(0,0,0);

    // Start is called before the first frame update
    void Start()
    {
        Mesh mesh = GetComponent<MeshFilter>().mesh;
        Vector3[] vertices = mesh.vertices;
        Vector2[] uvs = new Vector2[vertices.Length];
        Bounds bounds = mesh.bounds;
        print(bounds.center);
        print(bounds.extents);

        
        position = GetComponent<Renderer>().bounds.center;
    }

    // Update is called once per frame
    void Update()
    {
        Mesh mesh = GetComponent<MeshFilter>().mesh;
        Vector3[] vertices = mesh.vertices;
        Vector2[] uvs = new Vector2[vertices.Length];
        Bounds bounds = mesh.bounds;
        Debug.DrawLine(new Vector3(0,0,0), GetComponent<Renderer>().bounds.center, Color.red);
        Debug.DrawLine(GetComponent<Renderer>().bounds.center, GetComponent<Renderer>().bounds.center + GetComponent<Renderer>().bounds.extents, Color.blue);
        Debug.DrawLine(GetComponent<Renderer>().bounds.center, GetComponent<Renderer>().bounds.center - GetComponent<Renderer>().bounds.extents, Color.blue);
        position = GetComponent<Renderer>().bounds.center;
    }
}
