import { Fragment, useEffect, useRef, useState } from "react"
import { useRouter } from "next/router"
import { connect, E, getRefValue, isTrue, preventDefault, refs, set_val, updateState, uploadFiles } from "/utils/state"
import "focus-visible/dist/focus-visible"
import "gridjs/dist/theme/mermaid.css"
import { Button, Center, Heading, HStack, Input, Spinner, useColorMode, VStack } from "@chakra-ui/react"
import { Grid as DataTableGrid } from "gridjs-react"
import NextHead from "next/head"



export default function Component() {
  const [state, setState] = useState({"columns": ["title", "url", "summary"], "data": [], "is_hydrated": false, "is_working": false, "topic": "", "events": [{"name": "state.hydrate"}], "files": []})
  const [result, setResult] = useState({"state": null, "events": [], "processing": false})
  const router = useRouter()
  const socket = useRef(null)
  const { isReady } = router
  const { colorMode, toggleColorMode } = useColorMode()
  const focusRef = useRef();
  
  const Event = (events, _e) => {
      preventDefault(_e);
      setState({
        ...state,
        events: [...state.events, ...events],
      })
  }

  const File = files => setState({
    ...state,
    files,
  })

  useEffect(()=>{
    if(!isReady) {
      return;
    }
    if (!socket.current) {
      connect(socket, state, setState, result, setResult, router, ['websocket', 'polling'])
    }
    const update = async () => {
      if (result.state != null){
        setState({
          ...result.state,
          events: [...state.events, ...result.events],
        })

        setResult({
          state: null,
          events: [],
          processing: false,
        })
      }

      await updateState(state, setState, result, setResult, router, socket.current)
    }
    if (focusRef.current)
      focusRef.current.focus();
    update()
  })
  useEffect(() => {
    const change_complete = () => Event([E('state.hydrate', {})])
    router.events.on('routeChangeComplete', change_complete)
    return () => {
      router.events.off('routeChangeComplete', change_complete)
    }
  }, [router])


  return (
    <Center sx={{"paddingTop": "10%"}}>
  <VStack sx={{"width": "80%", "fontSize": "1em"}}>
  <Heading sx={{"fontSize": "2em"}}>
  {`뉴스 크롤링 & 요약 서비스`}
</Heading>
  <Input onBlur={_e => Event([E("state.set_topic", {value:_e.target.value})], _e)} placeholder="topic" type="text"/>
  <HStack>
  <Button onClick={_e => Event([E("state.handle_submit", {})], _e)}>
  {`시작`}
</Button>
  <Button onClick={_e => Event([E("state.export", {})], _e)}>
  {`excel로 export`}
</Button>
  <Button onClick={_e => Event([E("state.delete_all", {})], _e)}>
  {`모두 삭제`}
</Button>
</HStack>
  <Fragment>
  {isTrue(state.is_working) ? (
  <Fragment>
  <Spinner size="xl" speed="1.5s" sx={{"color": "lightgreen"}} thickness={5}/>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <DataTableGrid columns={state.columns} data={state.data} pagination={true} search={true} sort={false}/>
</VStack>
  <NextHead>
  <title>
  {`Pynecone App`}
</title>
  <meta content="A Pynecone app." name="description"/>
  <meta content="favicon.ico" property="og:image"/>
</NextHead>
</Center>
  )
}
