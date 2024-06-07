import { BsUpload, BsCaretRightFill } from 'react-icons/bs';
import { useState, useRef, useEffect  } from 'react';

export function Main() {

  const [paginas_totales, setPaginasTotales] = useState(0)
  const [cantidad_nodos, setCantidadNodos] = useState(0)
  const [paginas_nodo, setPaginasNodo] = useState(0)
  const [replicacion, setReplicacion] = useState(false)
  const [algoritmo_simulacion, setAlgoritmoSimmulacion] = useState('LRU')
  const [filename, setFilename] = useState("")
  const [stop_at, setStopAt] = useState(-1)
  const [file_commands, setFileCommands] = useState([])
  const [command_current_idx, setCommandCurrentIdx] = useState(0)
  const fileInputRef = useRef(null)
  const [interactive, setInteractive] = useState('');
  const [refs, setRefs] = useState([]);
  const [time, setTime] = useState(-1)
  const [interactiveMode, setInteractiveMode] = useState(false)
  const [cpus_stats, setCpusStats] = useState([]);
  const [indices_paginas, setIndicesPaginas] = useState([])
  const [paginas_en_nodo, setPaginasEnNodo] = useState([])

  const { ipcRenderer } = window.electron


  const cleanRefs = () => {
    setRefs([])
    setPaginasEnNodo([])
    setIndicesPaginas([])
    setTime(-1)
    setCpusStats([])
    setFilename('')
    setStopAt(-1)
    setFileCommands([])
  }

const extractLinesWithPageRefs = (text) => {
  // Split the text into lines, removing any leading/trailing whitespace
  const lines = text.trim().split(/\r?\n/); // Handle both CRLF and LF line endings

  // Filter lines containing "page_refs" (case-insensitive)
  const filteredLines = lines.filter(line => line.includes('page_refs'));

  return filteredLines;
}

const extractLinesWithIDs = (text) => {
  const lines = text.trim().split(/\r?\n/); // Handle both CRLF and LF line endings
  const filteredLines = lines.filter(line => line.includes('(ID:'));
  return filteredLines;
}


const  convertPageRefsToLists = (pageRefsString) => {
  // Remove leading/trailing whitespace and semicolons
  const cleanString = pageRefsString.trim().replace(/;$/, '').replace('page_refs = ', '');

  try {
    // Parse the string using eval (careful for security reasons)
    const parsedData = eval(cleanString);
    return parsedData;
  } catch (error) {
    console.error('Error parsing page refs string:', error);
    // Handle parsing errors (e.g., invalid JSON format)
    return []; // Or throw an error if needed
  }
}

const extractStats = (line) =>  {
  const regex = /stats: \[([0-9, ]+)\]/;
  const match = line.match(regex);
  if (match) {
    return match[1].split(',').map(Number);
  }
  return [];
}

const extractPages = (line) =>  {
  const regex = /pages: \[([0-9, ]+)\]/;
  const match = line.match(regex);
  if (match) {
    return match[1].split(',').map(Number);
  }
  return [];
}

const extractPagesIndexes = (line) =>  {
  const regex = /page_indexes: \[([0-9, ]+)\]/;
  const match = line.match(regex);
  if (match) {
    return match[1].split(',').map(Number);
  }
  return [];
}

function getPortionOfArray(arr, startIndex, endIndex) {
  // Check for valid indices (avoid out-of-bounds errors)
  if (startIndex >= 0 && startIndex < arr.length && endIndex > startIndex && endIndex <= arr.length) {
    return arr.slice(startIndex, endIndex);
  } else {
    // Handle invalid indices (optional: return empty array, throw error, etc.)
    return []; // Example: Return an empty array if indices are invalid
  }
}


const runPythonScript = async () => {
  try {
    const repl = replicacion ? 1 : 0
    const filename_refs = interactiveMode ? "interactive.txt" : filename 
    ipcRenderer.sendMessage('python-script', ["SOA.py", '--ui', '-a', algoritmo_simulacion, '-d',
     repl, '-o', 0, '-i', `${filename_refs}`, '-p', paginas_totales, '-q', paginas_nodo, '-n', cantidad_nodos]);
    ipcRenderer.once('python-script', (arg) => {
      // eslint-disable-next-line no-console
      console.log(arg)
      const page_refs = extractLinesWithPageRefs(arg)
      const cpus = extractLinesWithIDs(arg)
      const converted = page_refs.map(convertPageRefsToLists)

      
      const _time = interactiveMode ? converted.length - 1 : stop_at
      const indixes =  getPortionOfArray(cpus.map(extractStats), (_time) * cantidad_nodos, ( (_time) * cantidad_nodos) + parseInt(cantidad_nodos) )
      const pages =  getPortionOfArray(cpus.map(extractPages), (_time) * cantidad_nodos, ( (_time) * cantidad_nodos) + parseInt(cantidad_nodos) )
      const pages_indexes =  getPortionOfArray(cpus.map(extractPagesIndexes), (_time) * cantidad_nodos, ( (_time) * cantidad_nodos) + parseInt(cantidad_nodos) )
      setPaginasEnNodo(pages)
      setIndicesPaginas(pages_indexes)
      setCpusStats(indixes)
      setTime(_time)
      setRefs(converted)
    });
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }
};


  const create_node_pages = (current_ref, nodo) => {
    const node_pages = []
    // let n_size = 0
    // if (node_pages_array.length != 0) {
    //   node_pages_array = node_pages_array[node]
    //   n_size = node_pages_array.length  
    // }


    // for (let i = 0; i < n_size; i++) {
    //   node_pages.push(
    //     <div id={i.toString()} className={`pages-${node_pages_array[i][1]}`}>{node_pages_array[i][0]}</div>
    //   )
    // }
  
    // for (let i = n_size; i < paginas_nodo; i++) {
    //   node_pages.push(
    //     <div id={i.toString()} className='pages-empty'></div>
    //   )
    // }

    for (let i = 0; i < paginas_nodo; i++) {
      node_pages.push(
        <div id={i.toString()} className='pages-empty'></div>
      )
    }
    let n_size = 0
    if (indices_paginas.length != 0) 
      n_size = indices_paginas[nodo].length
    for (let i = 0; i < n_size; i++) {
      node_pages[indices_paginas[nodo][i]] = <div id={i.toString()} className={`pages-${current_ref[paginas_en_nodo[nodo][i]][1]}`}>{paginas_en_nodo[nodo][i]}</div>
    }



    return  <div className="cpu-pages">{node_pages}</div>
  }


  function getPageTypesForCpu(pages) {
    const cpus = []
    for (let i = 0; i < cantidad_nodos; i++) cpus.push([]) 

    for (let i = 0; i < pages.length; i++) {
      for (let j = 0; j < pages[i][0].length; j++) {
        const cpu = pages[i][0][j]
        cpus[cpu].push([i, pages[i][1]])

      }
    }
    return cpus
  }

  const create_nodes = () => {
    const nodos = []



    const current_ref = time !== -1 && refs.length > 0 ? refs[time] : []


    let nodes_p = []
    if (current_ref.length != 0)
      nodes_p = getPageTypesForCpu(refs[time])

    for (let i = 0; i < cantidad_nodos; i++) {
      nodos.push(
        <div id={i.toString()} className='cpu'>
          <div>
            <h3>Nodo {i}</h3>
          </div>
          {create_node_pages(current_ref, i)}
        </div>
      );
    }

    return <div className='memory-cpu'>{nodos}</div>;
  }

  const create_pages = () => {
    const paginas = []


    for (let i = 0; i < paginas_totales; i++) {
        paginas.push(<div id={i.toString()} className='pages'>{i}</div>)
    }
    return <div className='virtual-space'>{paginas}</div>
  }

  const create_stats = () => {
    const stats = []


    for (let i = 0; i < cpus_stats.length; i++) {
      stats.push(
          <div>
            <b>{`Nodo ${i}`}</b>
            <p title="Page-fault: Se da cuando un CPU desea referenciar una página y no la encuentra en ninguno de sus frames, por lo que debe buscarla en la memoria virtual y utilizar un algoritmo de reemplazo si todos sus frames contienen una página.">Page-faults: {cpus_stats[i][0]}</p>
            <p title="Hit: Se da cuando un CPU desea referenciar una página y la encuentra en almacenada en uno de sus frames, por lo que no es necesario que realicé una búsqueda en la memoria virtual ni utilice algoritmos de reemplazo de páginas.">Hits: {cpus_stats[i][1]}</p>
            <p title="Page-invalidation: Se da cuando un CPU desea referenciar una página en modo de escritura (o en un sistema que no permite replicación) y esta se encuentra referenciada por otro(s) CPU, por lo que el CPU debe comunicar a los otros CPUs que invaliden sus copias locales de la página de interés. Para el caso de esta simulación, los CPUs invalidan páginas eliminándo sus copias locales.">Invalidations: {cpus_stats[i][2]}</p>
          </div>
        )
    }
    return <div>{stats}</div>
  }

  const handleFileChange = (event) => {
      
      const file = event.target.files[0];
      cleanRefs()
      setFilename(file.name)
      setCommandCurrentIdx(0)
      if (!file) return;
    
      const reader = new FileReader();
      reader.onload = (e) => {
        const fileContent = e.target.result;
        const content = fileContent.split(/\r?\n/)
        content.shift()
        setFileCommands(content)
      };
      reader.readAsText(file);
    };
  

  const correrSimulacion = () => {
    setCommandCurrentIdx(stop_at)
    runPythonScript()
  }

  const updateStatus = async (setStatus, value) => {
    // Simulate asynchronous operation
    await new Promise(resolve => setTimeout(resolve, 1000));
    setStatus(value);
  };


  const correrSimulacionInteractiva = async () => {
    const _commands = [...file_commands]
    _commands.push(interactive)
    setFileCommands(_commands)
    setStopAt(_commands.length-1)
    setCommandCurrentIdx(_commands.length-1)
    ipcRenderer.sendMessage('python-script', ["util.py", "interactive.txt", "0,0,0", ..._commands]);
    ipcRenderer.once('python-script', (arg) => {
      console.log(arg)
      runPythonScript()
    });

  }

  const cambiarConfig = (e, setAlgo) => {
    cleanRefs()
    setAlgo(e.target.value)

  }

  function sumAtEachIndex(arrays) {
    if (arrays.length === 0) return [0,0,0]
    // Determine the length of the longest sub-array
    const maxLength = Math.max(...arrays.map(arr => arr.length));
  
    // Initialize an array of zeros with the same length
    const result = new Array(maxLength).fill(0);
  
    // Sum the elements at each index
    arrays.forEach(subArray => {
      subArray.forEach((num, index) => {
        result[index] += num;
      });
    });
  
    return result;
  }

  const create_total = () => {
    const totals = sumAtEachIndex(cpus_stats)
    return <div title='Page-faults, Hits y Page-Invalidations'>
      {`(PF: ${totals[0]} - H: ${totals[1]} -  I: ${totals[2]})`}
    </div>
  }

  const changeInteractiveMode = (change) => {
    cleanRefs()
    setInteractiveMode(change)
    
  }

  return (
    <div>
      <div className='header-config'>
        <h1 style={{ textAlign: "center" }}>Simulación Memoria Compartida Distribuida (DSM)</h1>
      </div>

      <div>
        <h2>Configuración</h2>
        <div className='config-panel'>
          <div className='input-config'>
            Páginas totales
            <input value={paginas_totales} onChange={(e) => cambiarConfig(e, setPaginasTotales)} type='number'/>
          </div>
          <div className='input-config'>
            Cantidad de nodos
            <input value={cantidad_nodos} onChange={(e) => cambiarConfig(e, setCantidadNodos)} type='number' />
          </div>
          <div className='input-config'>
            Páginas por nodo
            <input  value={paginas_nodo} onChange={(e) => cambiarConfig(e, setPaginasNodo)} type='number' />
          </div>
          <div className='input-config'>
            Algoritmo de simulación
            <select value={algoritmo_simulacion} onChange={(e) => cambiarConfig(e, setAlgoritmoSimmulacion)} name="algo" id="algo">
              <option title="LRU: Algoritmo de reemplazo Least Recently Used, a la hora de realizar un reemplazo de página en un CPU, el frame utilizado será el que fue utilizado por última vez una mayor cantidad de iteraciones (unidades de tiempo) atrás." value="LRU">LRU</option>
              <option title="Optimal: Algoritmo de reemplazo óptimo,  a la hora de realizar un reemplazo de página en un CPU, el frame utilizado será el que contenga la página que será utilizada dentro de la mayor cantidad de iteraciones (unidades de tiempo) adelate." value="OPTIMAL">Óptimo</option>
              <option title="FIFO: Algoritmo de reemplazo First-In-First-Out, a la hora de realizar un remplazo de página en un CPU, el frame utilizado será el que ha alocado una página una mayor cantidad de iteraciones (unidades de tiempo) atrás." value="FIFO">FIFO</option>
            </select>
          </div>
          <div className='input-config' title='Replicación: Para mejorar el rendimiento del sistema DSM básico, esta opción permite que las páginas que son read-only (referenciadas en modo lectura) puedan ser copiadas en tantos CPUs como las requieran, sin necesidad de invalidarlas cada vez que otro CPU desea referenciarlas.'>
            Replicación
            <input type='checkbox' checked={replicacion}  onChange={(e) => {
              cleanRefs()
              setReplicacion(e.target.checked)
            }} />
          </div>
        </div>
      </div>

      <div>
        <h2 title="Espacio Virtual: Representa la memoria virtual del sistema, accesible por todos los CPUs que deseen referenciar una página en modo de lectura o escritura.">Espacio virtual</h2>
        {create_pages()}
      </div>

      <div>
        <h2>Memorias (por nodo)</h2>
        {create_nodes()}
      </div>
      <div>
        <h2>Referencias</h2>
        <div className='ref-control-panel'>
          <button onClick={(e) => { 
            document.getElementById('upload-id').value = ''
            fileInputRef.current.click()
          }} disabled={interactiveMode} className='upload-button'><BsUpload style={{padding: "0 1rem 0 0"}} size="1.5em" />Subir Archivo</button>
          <input
            type="file"
            id='upload-id'
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={(handleFileChange)}
          />
          <button className='upload-button' disabled={interactiveMode} onClick={correrSimulacion}><BsCaretRightFill style={{padding: "0 1rem 0 0"}} size="1.5em" /> Ejecutar</button>
          <div style={{fontSize: 'small', paddingRight: '0.5rem'}}>Detenerse en</div>
          <input value={stop_at} disabled={interactiveMode} onChange={(e) => setStopAt(parseInt(e.target.value))} type='number'></input>
          <div style={{fontSize: 'small', padding: '0 0.5rem'}}>Agregar paso ({"<Nodo>,<Pagina>,<Modo> e.g. 2,4,r"})</div>
          <input disabled={!interactiveMode} style={{marginRight: '1rem'}} value={interactive} onChange={(e) => setInteractive(e.target.value)}></input>
          <button disabled={!interactiveMode} className='upload-button' onClick={correrSimulacionInteractiva}><BsCaretRightFill style={{padding: "0 1rem 0 0"}} size="1.5em" /> Insertar</button>
          <div title="Simular paso por paso" style={{fontSize: 'small', padding: '0 0.5rem'}}>Modo Interactivo</div>
          <input type='checkbox' checked={interactiveMode}  onChange={(e) => changeInteractiveMode(e.target.checked)} />
        </div>
      </div>
      {filename}
      <div style={{display: "flex"}}>
        <div  style={{ background: "#ccc", height: "32vh", width: "50%", overflowY:"auto", margin: "2rem"}}>
          {file_commands.map((command, index) => {
            
            const div_style = {display: "flex", padding: "0.2rem", fontFamily: "monospace", whiteSpace: "pre-line", textAlign: "start", cursor: "pointer"}

            if (stop_at === index) 
              div_style.background = "#daa"

            if (command_current_idx === index)
              div_style.background = "#aaa"

             
            return <div style={div_style}>
              <div style={{paddingRight: "2.5rem"}}>{index}</div>
              <div style={{width: "100%"}} onClick={() => {
                if (interactiveMode) return
                setStopAt(index)
              }}>{command}</div>
            </div>
            }
          )}
        </div>
        <div style={{width: "50%"}}>
          <div style={{paddingLeft: "1rem"}}>
            <b>Estadísticas</b>
            {create_total()}   
          </div>         
          <div style={{ padding: "1rem", background: "#ddd", height: "26.5vh",overflowY:"auto", margin: "0.8rem"}} >
            {create_stats()}
          </div>
        </div>
      </div>

    </div>
  );
}
